from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_operator
from app.models.violation import Violation, ViolationType, ViolationStatus
from app.models.user import User
from app.schemas.violation import ViolationResponse, ViolationUpdate

router = APIRouter(prefix="/violations", tags=["Violations"])


@router.get("/", response_model=List[ViolationResponse])
async def list_violations(
    violation_type: Optional[ViolationType] = Query(None),
    status: Optional[ViolationStatus] = Query(None),
    plate_number: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = []
    if violation_type:
        filters.append(Violation.violation_type == violation_type)
    if status:
        filters.append(Violation.status == status)
    if plate_number:
        filters.append(Violation.plate_number.ilike(f"%{plate_number}%"))
    if date_from:
        filters.append(Violation.detected_at >= date_from)
    if date_to:
        filters.append(Violation.detected_at <= date_to)

    query = select(Violation).order_by(Violation.detected_at.desc())
    if filters:
        query = query.where(and_(*filters))

    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{violation_id}", response_model=ViolationResponse)
async def get_violation(
    violation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Violation).where(Violation.id == violation_id))
    violation = result.scalar_one_or_none()
    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")
    return violation


@router.patch("/{violation_id}", response_model=ViolationResponse)
async def update_violation(
    violation_id: UUID,
    payload: ViolationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator),
):
    result = await db.execute(select(Violation).where(Violation.id == violation_id))
    violation = result.scalar_one_or_none()
    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")

    if payload.status:
        violation.status = payload.status
        violation.reviewed_by = current_user.id
        violation.reviewed_at = datetime.utcnow()
    if payload.notes is not None:
        violation.notes = payload.notes

    await db.commit()
    await db.refresh(violation)
    return violation


@router.delete("/{violation_id}", status_code=204)
async def delete_violation(
    violation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator),
):
    result = await db.execute(select(Violation).where(Violation.id == violation_id))
    violation = result.scalar_one_or_none()
    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")
    await db.delete(violation)
    await db.commit()
    