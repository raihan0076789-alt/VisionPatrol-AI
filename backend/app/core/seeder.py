import uuid
from datetime import datetime, timedelta
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.violation import Violation, ViolationType, ViolationStatus
from app.models.challan import Challan, ChallanStatus
from app.models.camera import Camera
from app.models.detection_session import DetectionSession, SessionStatus
from app.models.vehicle import Vehicle, VehicleType


SAMPLE_PLATES = [
    "KL65AB1234", "KL07CD5678", "KL01EF9012",
    "TN09GH3456", "TN22IJ7890", "MH12KL2345",
    "MH01MN6789", "DL05OP0123", "DL08QR4567",
    "KA03ST8901",
]

VIOLATION_TYPES = list(ViolationType)
LOCATIONS = [
    "NH-66 Tirur Junction", "Malappuram Bypass",
    "Calicut Road Checkpoint", "Tirur Town Center",
    "Ponnani Highway", "Kuttippuram Bridge",
]


async def seed_sample_data(db: AsyncSession):
    # Check if data already exists
    result = await db.execute(select(Violation))
    if result.scalars().first():
        print("Sample data already exists, skipping seed")
        return

    print("Seeding sample data...")

    # Create a camera
    camera = Camera(
        name="Camera-01 NH66",
        location="NH-66 Tirur Junction",
        latitude=10.9124,
        longitude=75.9220,
        is_active=True,
    )
    db.add(camera)
    await db.flush()

    # Create a detection session
    session = DetectionSession(
        camera_id=camera.id,
        video_filename="sample_traffic.mp4",
        status=SessionStatus.completed,
        total_frames=1500,
        processed_frames=1500,
        violations_found=15,
        completed_at=datetime.utcnow(),
    )
    db.add(session)
    await db.flush()

    # Create vehicles
    vehicles = []
    for plate in SAMPLE_PLATES:
        vehicle = Vehicle(
            plate_number=plate,
            owner_name=f"Owner {plate[-4:]}",
            owner_phone=f"98{random.randint(10000000, 99999999)}",
            vehicle_type=random.choice(list(VehicleType)),
        )
        db.add(vehicle)
        vehicles.append(vehicle)
    await db.flush()

    # Create violations over last 30 days
    challans_to_create = []
    challan_count = 0

    for i in range(40):
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        detected_at = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago)

        vehicle = random.choice(vehicles)
        v_type = random.choice(VIOLATION_TYPES)
        status = random.choice([
            ViolationStatus.pending,
            ViolationStatus.confirmed,
            ViolationStatus.confirmed,
            ViolationStatus.challan_issued,
            ViolationStatus.dismissed,
        ])

        violation = Violation(
            session_id=session.id,
            vehicle_id=vehicle.id,
            violation_type=v_type,
            status=status,
            confidence_score=round(random.uniform(0.65, 0.99), 3),
            plate_number=vehicle.plate_number,
            location=random.choice(LOCATIONS),
            detected_at=detected_at,
        )
        db.add(violation)
        await db.flush()

        # Create challan for challan_issued violations
        if status == ViolationStatus.challan_issued:
            challan_count += 1
            fine_map = {
                ViolationType.helmet: 1000.0,
                ViolationType.triple_riding: 2000.0,
                ViolationType.signal_jump: 1000.0,
                ViolationType.wrong_side: 5000.0,
                ViolationType.no_plate: 500.0,
                ViolationType.over_speed: 2000.0,
            }
            challan_status = random.choice([
                ChallanStatus.generated,
                ChallanStatus.served,
                ChallanStatus.paid,
            ])
            challan = Challan(
                challan_number=f"VP{datetime.utcnow().strftime('%Y%m%d')}{str(challan_count).zfill(5)}",
                violation_id=violation.id,
                vehicle_id=vehicle.id,
                fine_amount=fine_map.get(v_type, 500.0),
                status=challan_status,
                due_date=detected_at + timedelta(days=30),
                paid_at=datetime.utcnow() if challan_status == ChallanStatus.paid else None,
            )
            db.add(challan)

    await db.commit()
    print("✅ Sample data seeded successfully — 40 violations, cameras, vehicles created")
    