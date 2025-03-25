from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime

class DigestBase(BaseModel):
    resolution_summary: Optional[str] = None
    media_path: Optional[str] = None
    insights: Optional[Dict[str, str]] = None

class DigestCreate(DigestBase):
    pass

class DigestResponse(DigestBase):
    id: int
    uuid: str
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True  # For newer Pydantic versions
