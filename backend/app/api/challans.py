from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from uuid import UUID
from datetime import datetime, timedelta
import os

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_operator
from app.models.challan import Challan, ChallanStatus
from app.models.violation import Violation, ViolationStatus, ViolationType
from app.models.user import User
from app.schemas.challan import ChallanResponse, ChallanUpdate
from app.services.challan_service import generate_challan_pdf

router = APIRouter(prefix="/challans", tags=["Challans"])

# Fine amounts per violation type
FINE_AMOUNTS = {
    ViolationType.helmet: 1000.0,
    ViolationType.triple_riding: 2000.0,
    ViolationType.signal_jump: 1000.0,
    ViolationType.wrong_side: 5000.0,
    ViolationType.no_plate: 500.0,
    ViolationType.over_speed: 2000.0,
}


async def generate_challan_number(db: AsyncSession) -> str:
    result = await db.execute(select(func.count(Challan.id)))
    count = result.scalar() or 0
    today = datetime.utcnow().strftime("%Y%m%d")
    return f"VP{today}{str(count + 1).zfill(5)}"


@router.post("/generate/{violation_id}", response_model=ChallanResponse, status_code=201)
async def generate_challan(
    violation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator),
):
    # Get violation
    result = await db.execute(select(Violation).where(Violation.id == violation_id))
    violation = result.scalar_one_or_none()
    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")

    # Check if challan already exists
    existing = await db.execute(select(Challan).where(Challan.violation_id == violation_id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Challan already generated for this violation")

    challan_number = await generate_challan_number(db)
    fine_amount = FINE_AMOUNTS.get(violation.violation_type, 500.0)

    challan = Challan(
        challan_number=challan_number,
        violation_id=violation_id,
        vehicle_id=violation.vehicle_id,
        fine_amount=fine_amount,
        due_date=datetime.utcnow() + timedelta(days=30),
        status=ChallanStatus.generated,
    )
    db.add(challan)

    # Update violation status
    violation.status = ViolationStatus.challan_issued
    await db.commit()
    await db.refresh(challan)

    # Generate PDF in background
    pdf_path = await generate_challan_pdf(challan, violation)
    if pdf_path:
        challan.pdf_path = pdf_path
        await db.commit()

    return challan


@router.get("/", response_model=List[ChallanResponse])
async def list_challans(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Challan).order_by(Challan.created_at.desc()))
    return result.scalars().all()


@router.get("/{challan_id}", response_model=ChallanResponse)
async def get_challan(
    challan_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Challan).where(Challan.id == challan_id))
    challan = result.scalar_one_or_none()
    if not challan:
        raise HTTPException(status_code=404, detail="Challan not found")
    return challan


@router.get("/{challan_id}/download")
async def download_challan_pdf(
    challan_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Challan).where(Challan.id == challan_id))
    challan = result.scalar_one_or_none()
    if not challan or not challan.pdf_path:
        raise HTTPException(status_code=404, detail="Challan PDF not found")
    if not os.path.exists(challan.pdf_path):
        raise HTTPException(status_code=404, detail="PDF file missing on disk")
    return FileResponse(challan.pdf_path, media_type="application/pdf",
                       filename=f"{challan.challan_number}.pdf")


@router.patch("/{challan_id}", response_model=ChallanResponse)
async def update_challan(
    challan_id: UUID,
    payload: ChallanUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator),
):
    result = await db.execute(select(Challan).where(Challan.id == challan_id))
    challan = result.scalar_one_or_none()
    if not challan:
        raise HTTPException(status_code=404, detail="Challan not found")

    if payload.status:
        challan.status = payload.status
        if payload.status == ChallanStatus.paid:
            challan.paid_at = datetime.utcnow()
        elif payload.status == ChallanStatus.served:
            challan.served_at = datetime.utcnow()

    await db.commit()
    await db.refresh(challan)
    return challan