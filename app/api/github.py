from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.verification import VerificationResponse

from app.services.github_verification_service import verify_github


router = APIRouter(
    prefix="/verify",
    tags=["GitHub Verification"]
)


@router.post(
    "/github/{resume_id}",
    response_model=VerificationResponse
)
def github_verify(
    resume_id: int,
    github_username: str,
    db: Session = Depends(get_db)
):

    return verify_github(
        db=db,
        resume_id=resume_id,
        github_username=github_username
    )