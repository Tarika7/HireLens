from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.matching import MatchingResponse
from app.services.matching_service import run_matching

router = APIRouter(
    prefix="/matching",
    tags=["AI Matching"]
)


@router.post(
    "/run/{resume_id}",
    response_model=MatchingResponse
)
def run_ai_matching(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """
    Run AI semantic matching
    for a resume.
    """

    return run_matching(
        db=db,
        resume_id=resume_id
    )