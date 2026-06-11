import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class EvidenceType(str, enum.Enum):
    frame_image = "frame_image"
    video_clip = "video_clip"
    plate_crop = "plate_crop"
    annotated_image = "annotated_image"


class Evidence(Base):
    __tablename__ = "evidence_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    violation_id = Column(UUID(as_uuid=True), ForeignKey("violations.id"), nullable=False)
    evidence_type = Column(Enum(EvidenceType), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size_kb = Column(Integer, nullable=True)
    frame_number = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    violation = relationship("Violation", back_populates="evidence")