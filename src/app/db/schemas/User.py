from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    uuid: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True
