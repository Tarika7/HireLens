from fastapi import FastAPI

from app.database.database import create_tables

# Import models
from app.models.user import User
from app.models.job import Job

from app.api.auth import router as auth_router
from app.api.jobs import router as job_router

app = FastAPI(
    title="HireLens",
    description="AI-Powered Resume Verification & Recruitment Platform",
    version="1.0.0"
)

@app.on_event("startup")
def startup():
    create_tables()

app.include_router(auth_router)
app.include_router(job_router)


@app.get("/")
def root():
    return {"message": "HireLens API is running"}