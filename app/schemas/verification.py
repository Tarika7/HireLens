from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class VerificationResponse(BaseModel):

    id: int

    resume_id: int

    verification_type: str

    status: str

    score: Optional[float] = None

    details: Optional[dict] = None

    created_at: datetime

    class Config:
        from_attributes = True