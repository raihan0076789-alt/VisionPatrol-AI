import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class ViolationType(str, enum.Enum):
    helmet = "helmet"
    triple_riding = "triple_riding"
    signal_jump = "signal_jump"
    wrong_side = "wrong_side"
    no_plate = "no_plate"
    over_speed = "over_speed"


class ViolationStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    dismissed = "dismissed"
    challan_issued = "challan_issued"


class Violation(Base):
    __tablename__ = "violations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("detection_sessions.id"), nullable=True)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    violation_type = Column(Enum(ViolationType), nullable=False)
    status = Column(Enum(ViolationStatus), default=ViolationStatus.pending)
    confidence_score = Column(Float, nullable=False)
    plate_number = Column(String(20), nullable=True, index=True)
    location = Column(String(255), nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    reviewed_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    session = relationship("DetectionSession", back_populates="violations")
    vehicle = relationship("Vehicle", back_populates="violations")
    reviewed_by_user = relationship("User", back_populates="violations")
    evidence = relationship("Evidence", back_populates="violation")
    challan = relationship("Challan", back_populates="violation", uselist=False)