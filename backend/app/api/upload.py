from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
import uuid
import aiofiles
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import require_operator
from app.core.config import settings
from app.models.user import User
from app.models.detection_session import DetectionSession, SessionStatus
from app.models.camera import Camera

router = APIRouter(prefix="/upload", tags=["Upload"])

ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}
MAX_SIZE_BYTES = settings.MAX_FILE_SIZE_MB * 1024 * 1024


async def process_video_background(session_id: str, video_path: str):
    """
    Background task — runs ML detection on uploaded video.
    For now creates mock violations. Replace with real ViolationDetector later.
    """
    from app.core.database import AsyncSessionLocal
    from app.models.violation import Violation, ViolationType, ViolationStatus
    from app.models.vehicle import Vehicle, VehicleType
    import random

    async with AsyncSessionLocal() as db:
        try:
            # Update session to processing
            result = await db.execute(
                select(DetectionSession).where(DetectionSession.id == session_id)
            )
            session = result.scalar_one_or_none()
            if not session:
                return

            session.status = SessionStatus.processing
            await db.commit()

            # Simulate processing delay
            import asyncio
            await asyncio.sleep(3)

            # Create mock detected violations
            mock_violations = [
                {"type": ViolationType.helmet, "confidence": 0.92, "plate": "KL65AB1234"},
                {"type": ViolationType.triple_riding, "confidence": 0.87, "plate": "TN09GH3456"},
                {"type": ViolationType.no_plate, "confidence": 0.78, "plate": None},
            ]

            violations_created = 0
            for v_data in mock_violations:
                # Create or get vehicle
                vehicle = None
                if v_data["plate"]:
                    v_result = await db.execute(
                        select(Vehicle).where(Vehicle.plate_number == v_data["plate"])
                    )
                    vehicle = v_result.scalar_one_or_none()
                    if not vehicle:
                        vehicle = Vehicle(
                            plate_number=v_data["plate"],
                            vehicle_type=VehicleType.motorcycle,
                        )
                        db.add(vehicle)
                        await db.flush()

                violation = Violation(
                    session_id=session_id,
                    vehicle_id=vehicle.id if vehicle else None,
                    violation_type=v_data["type"],
                    status=ViolationStatus.pending,
                    confidence_score=v_data["confidence"],
                    plate_number=v_data["plate"],
                    location=session.camera.location if session.camera else "Uploaded Video",
                    detected_at=datetime.utcnow(),
                )
                db.add(violation)
                violations_created += 1

            # Mark session complete
            session.status = SessionStatus.completed
            session.violations_found = violations_created
            session.completed_at = datetime.utcnow()
            await db.commit()
            print(f"✅ Video processed: {violations_created} violations found")

        except Exception as e:
            print(f"❌ Video processing error: {e}")
            if session:
                session.status = SessionStatus.failed
                await db.commit()


@router.post("/video")
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator),
):
    # Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {ALLOWED_EXTENSIONS}"
        )

    # Save file
    file_id = str(uuid.uuid4())
    save_path = f"{settings.UPLOAD_DIR}/videos/{file_id}{ext}"

    os.makedirs(f"{settings.UPLOAD_DIR}/videos", exist_ok=True)

    async with aiofiles.open(save_path, "wb") as out_file:
        content = await file.read()
        if len(content) > MAX_SIZE_BYTES:
            raise HTTPException(status_code=400, detail="File too large")
        await out_file.write(content)

    # Create detection session
    session = DetectionSession(
        video_filename=file.filename,
        video_path=save_path,
        status=SessionStatus.pending,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    # Start background processing
    background_tasks.add_task(
        process_video_background,
        str(session.id),
        save_path,
    )

    return {
        "session_id": str(session.id),
        "filename": file.filename,
        "status": "processing",
        "message": "Video uploaded successfully. Processing started.",
    }


@router.get("/sessions")
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator),
):
    result = await db.execute(
        select(DetectionSession).order_by(DetectionSession.started_at.desc()).limit(20)
    )
    sessions = result.scalars().all()
    return [
        {
            "id": str(s.id),
            "filename": s.video_filename,
            "status": s.status.value,
            "violations_found": s.violations_found,
            "started_at": s.started_at.isoformat(),
            "completed_at": s.completed_at.isoformat() if s.completed_at else None,
        }
        for s in sessions
    ]


@router.get("/sessions/{session_id}/status")
async def session_status(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator),
):
    result = await db.execute(
        select(DetectionSession).where(DetectionSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "id": str(session.id),
        "status": session.status.value,
        "violations_found": session.violations_found,
        "completed_at": session.completed_at.isoformat() if session.completed_at else None,
    }