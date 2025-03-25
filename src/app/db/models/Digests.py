from sqlalchemy import Column, Integer, String, ForeignKey, Text, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from db.models.Base import Base, BaseModel

class Digest(Base, BaseModel):
    __tablename__ = "digests"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resolution_summary = Column(Text, nullable=True)
    media_path = Column(String(512), nullable=True)
    insights = Column(JSON, nullable=True)

    # Relationship to User
    user = relationship("User", back_populates="digests")

    # Table constraints
    __table_args__ = (UniqueConstraint("user_id"),)
