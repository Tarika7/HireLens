from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MatchingResponse(BaseModel):

    id: int

    resume_id: int

    job_id: int

    match_score: float

    match_reasons: dict

    confidence_score: Optional[float] = None

    evidence_coverage: Optional[float] = None

    recommendation: Optional[str] = None

    confidence_reasons: Optional[dict] = None

    created_at: datetime

    class Config:
        from_attributes = True