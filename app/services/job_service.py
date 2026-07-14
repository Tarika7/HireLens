from sqlalchemy.orm import Session

from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate


# Create a new job
def create_job(db: Session, recruiter_id: int, job: JobCreate):
    new_job = Job(
        recruiter_id=recruiter_id,
        title=job.title,
        description_text=job.description_text,
        required_skills=job.required_skills
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job


# Get all jobs of the logged-in recruiter
def get_jobs(db: Session, recruiter_id: int):
    return (
        db.query(Job)
        .filter(Job.recruiter_id == recruiter_id)
        .all()
    )


# Get one specific job
def get_job(db: Session, recruiter_id: int, job_id: int):
    return (
        db.query(Job)
        .filter(
            Job.id == job_id,
            Job.recruiter_id == recruiter_id
        )
        .first()
    )


# Update a job
def update_job(db: Session, recruiter_id: int, job_id: int, updated_job: JobUpdate):

    job = get_job(db, recruiter_id, job_id)

    if not job:
        return None

    if updated_job.title is not None:
        job.title = updated_job.title

    if updated_job.description_text is not None:
        job.description_text = updated_job.description_text

    if updated_job.required_skills is not None:
        job.required_skills = updated_job.required_skills

    db.commit()
    db.refresh(job)

    return job


# Delete a job
def delete_job(db: Session, recruiter_id: int, job_id: int):

    job = get_job(db, recruiter_id, job_id)

    if not job:
        return False

    db.delete(job)
    db.commit()

    return True