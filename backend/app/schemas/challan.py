from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.challan import ChallanStatus


class ChallanResponse(BaseModel):
    id: UUID
    challan_number: str
    fine_amount: float
    status: ChallanStatus
    due_date: Optional[datetime]
    created_at: datetime
    pdf_path: Optional[str]

    class Config:
        from_attributes = True


class ChallanUpdate(BaseModel):
    status: Optional[ChallanStatus] = None