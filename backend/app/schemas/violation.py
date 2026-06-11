from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.violation import ViolationType, ViolationStatus


class ViolationResponse(BaseModel):
    id: UUID
    violation_type: ViolationType
    status: ViolationStatus
    confidence_score: float
    plate_number: Optional[str]
    location: Optional[str]
    detected_at: datetime
    notes: Optional[str]

    class Config:
        from_attributes = True


class ViolationUpdate(BaseModel):
    status: Optional[ViolationStatus] = None
    notes: Optional[str] = None


class ViolationFilter(BaseModel):
    violation_type: Optional[ViolationType] = None
    status: Optional[ViolationStatus] = None
    plate_number: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    