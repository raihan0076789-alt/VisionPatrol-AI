from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.violation import Violation, ViolationType, ViolationStatus
from app.models.challan import Challan, ChallanStatus
from app.models.user import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary")
async def get_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = datetime.utcnow().replace(hour=0, minute=0, second=0)

    # Total violations today
    today_result = await db.execute(
        select(func.count(Violation.id)).where(Violation.detected_at >= today)
    )
    today_count = today_result.scalar() or 0

    # Total violations all time
    total_result = await db.execute(select(func.count(Violation.id)))
    total_count = total_result.scalar() or 0

    # Pending violations
    pending_result = await db.execute(
        select(func.count(Violation.id)).where(Violation.status == ViolationStatus.pending)
    )
    pending_count = pending_result.scalar() or 0

    # Total challans
    challan_result = await db.execute(select(func.count(Challan.id)))
    challan_count = challan_result.scalar() or 0

    # Total fines collected
    fines_result = await db.execute(
        select(func.sum(Challan.fine_amount)).where(Challan.status == ChallanStatus.paid)
    )
    fines_collected = fines_result.scalar() or 0

    return {
        "today_violations": today_count,
        "total_violations": total_count,
        "pending_violations": pending_count,
        "total_challans": challan_count,
        "fines_collected": fines_collected,
    }


@router.get("/violations-by-type")
async def violations_by_type(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    since = datetime.utcnow() - timedelta(days=days)
    result = await db.execute(
        select(Violation.violation_type, func.count(Violation.id).label("count"))
        .where(Violation.detected_at >= since)
        .group_by(Violation.violation_type)
    )
    return [{"type": row[0].value, "count": row[1]} for row in result.all()]


@router.get("/violations-by-day")
async def violations_by_day(
    days: int = Query(30, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    since = datetime.utcnow() - timedelta(days=days)
    result = await db.execute(
        select(
            func.date(Violation.detected_at).label("date"),
            func.count(Violation.id).label("count")
        )
        .where(Violation.detected_at >= since)
        .group_by(func.date(Violation.detected_at))
        .order_by(func.date(Violation.detected_at))
    )
    return [{"date": str(row[0]), "count": row[1]} for row in result.all()]


@router.get("/top-offenders")
async def top_offenders(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Violation.plate_number, func.count(Violation.id).label("count"))
        .where(Violation.plate_number.isnot(None))
        .group_by(Violation.plate_number)
        .order_by(func.count(Violation.id).desc())
        .limit(limit)
    )
    return [{"plate": row[0], "count": row[1]} for row in result.all()]