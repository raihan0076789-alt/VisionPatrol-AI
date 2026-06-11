from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.vehicle import VehicleType


class VehicleCreate(BaseModel):
    plate_number: str
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    owner_email: Optional[str] = None
    owner_address: Optional[str] = None
    vehicle_type: VehicleType = VehicleType.other
    vehicle_model: Optional[str] = None
    vehicle_color: Optional[str] = None


class VehicleUpdate(BaseModel):
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    owner_email: Optional[str] = None
    owner_address: Optional[str] = None
    vehicle_type: Optional[VehicleType] = None
    vehicle_model: Optional[str] = None
    vehicle_color: Optional[str] = None


class VehicleResponse(BaseModel):
    id: UUID
    plate_number: str
    owner_name: Optional[str]
    owner_phone: Optional[str]
    owner_email: Optional[str]
    vehicle_type: VehicleType
    vehicle_model: Optional[str]
    vehicle_color: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True