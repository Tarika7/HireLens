from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class JobCreate(BaseModel):
    title: str
    description_text: str
    required_skills: Optional[str] = None


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description_text: Optional[str] = None
    required_skills: Optional[str] = None


class JobResponse(BaseModel):
    id: int
    title: str
    description_text: str
    required_skills: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True