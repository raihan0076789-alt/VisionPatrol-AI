import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class SessionStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class DetectionSession(Base):
    __tablename__ = "detection_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_id = Column(UUID(as_uuid=True), ForeignKey("cameras.id"), nullable=True)
    video_filename = Column(String(500), nullable=True)
    video_path = Column(String(1000), nullable=True)
    status = Column(Enum(SessionStatus), default=SessionStatus.pending)
    total_frames = Column(Integer, default=0)
    processed_frames = Column(Integer, default=0)
    violations_found = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    camera = relationship("Camera", back_populates="sessions")
    violations = relationship("Violation", back_populates="session")