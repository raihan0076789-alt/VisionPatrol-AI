import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class VehicleType(str, enum.Enum):
    motorcycle = "motorcycle"
    car = "car"
    truck = "truck"
    bus = "bus"
    auto = "auto"
    other = "other"


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plate_number = Column(String(20), unique=True, nullable=False, index=True)
    owner_name = Column(String(100), nullable=True)
    owner_phone = Column(String(15), nullable=True)
    owner_email = Column(String(255), nullable=True)
    owner_address = Column(String(500), nullable=True)
    vehicle_type = Column(Enum(VehicleType), default=VehicleType.other)
    vehicle_model = Column(String(100), nullable=True)
    vehicle_color = Column(String(50), nullable=True)
    registration_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    violations = relationship("Violation", back_populates="vehicle")
    challans = relationship("Challan", back_populates="vehicle")