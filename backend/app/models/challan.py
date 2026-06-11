import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class ChallanStatus(str, enum.Enum):
    generated = "generated"
    served = "served"
    paid = "paid"
    cancelled = "cancelled"
    disputed = "disputed"


class Challan(Base):
    __tablename__ = "challans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    challan_number = Column(String(20), unique=True, nullable=False, index=True)
    violation_id = Column(UUID(as_uuid=True), ForeignKey("violations.id"), nullable=False)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=True)

    fine_amount = Column(Float, nullable=False)
    status = Column(Enum(ChallanStatus), default=ChallanStatus.generated)
    pdf_path = Column(String(1000), nullable=True)
    due_date = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    served_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    violation = relationship("Violation", back_populates="challan")
    vehicle = relationship("Vehicle", back_populates="challans")