from sqlalchemy import Column, Integer, String, ForeignKey, Text, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from db.models.Base import Base, BaseModel
from enum import Enum

class DigestStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Digest(Base, BaseModel):
    __tablename__ = "digests"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(256), nullable=True)  # Optional title for the digest
    resolution_summary = Column(Text, nullable=True)
    media_path = Column(String(512), nullable=True)  # Path to zip file
    insights = Column(JSON, nullable=True)  # File insights
    status = Column(String(20), default=DigestStatus.PENDING.value)
    total_files = Column(Integer, default=0)
    processed_files = Column(Integer, default=0)

    # Relationship to User
    user = relationship("User", back_populates="digests")
