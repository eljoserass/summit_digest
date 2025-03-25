from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db.models.Base import Base, BaseModel

class User(Base, BaseModel):
    __tablename__ = "users"

    username = Column(String(256), unique=True, nullable=False, index=True)
    email = Column(String(256), nullable=True)
    password = Column(String(256), nullable=False)

    # Relationship - we'll use string reference to avoid circular imports
    digests = relationship("Digest", back_populates="user")
