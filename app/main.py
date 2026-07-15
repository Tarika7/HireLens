from fastapi import FastAPI

from app.database.database import create_tables

# Import models
from app.models.user import User
from app.models.job import Job

from app.api.auth import router as auth_router
from app.api.jobs import router as job_router
from app.models.resume import Resume
from app.api.resumes import router as resume_router
from app.models.parsed_resume import ParsedResume
from app.api.matching import router as matching_router


app = FastAPI(
    title="HireLens",
    description="AI-Powered Resume Verification & Recruitment Platform",
    version="1.0.0"
)

app.include_router(resume_router)

@app.on_event("startup")
def startup():
    create_tables()

app.include_router(auth_router)
app.include_router(job_router)
app.include_router(matching_router)


@app.get("/")
def root():
    return {"message": "HireLens API is running"}