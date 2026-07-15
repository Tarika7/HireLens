from datetime import datetime
from pydantic import BaseModel


class ResumeResponse(BaseModel):
    id: int
    recruiter_id: int
    job_id: int
    original_filename: str
    stored_filename: str
    file_path: str
    parsing_status: str
    created_at: datetime

    class Config:
        from_attributes = True