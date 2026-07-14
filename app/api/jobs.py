from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.job import JobCreate, JobUpdate, JobResponse
from app.services.auth_service import get_current_user
from app.services import job_service

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


# Create Job
@router.post(
    "/",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED
)
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return job_service.create_job(
        db=db,
        recruiter_id=current_user.id,
        job=job
    )


# Get All Jobs
@router.get(
    "/",
    response_model=list[JobResponse]
)
def get_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return job_service.get_jobs(
        db=db,
        recruiter_id=current_user.id
    )


# Get Single Job
@router.get(
    "/{job_id}",
    response_model=JobResponse
)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    job = job_service.get_job(
        db=db,
        recruiter_id=current_user.id,
        job_id=job_id
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found."
        )

    return job


# Update Job
@router.put(
    "/{job_id}",
    response_model=JobResponse
)
def update_job(
    job_id: int,
    updated_job: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    job = job_service.update_job(
        db=db,
        recruiter_id=current_user.id,
        job_id=job_id,
        updated_job=updated_job
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found."
        )

    return job


# Delete Job
@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    deleted = job_service.delete_job(
        db=db,
        recruiter_id=current_user.id,
        job_id=job_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Job not found."
        )

    return {
        "message": "Job deleted successfully."
    }