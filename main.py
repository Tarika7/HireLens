from fastapi import FastAPI
from app.routes.auth import router as auth_router

# Create the FastAPI application
app = FastAPI(
    title="HireLens",
    description="AI-Powered Resume Verification & Recruitment Platform",
    version="1.0.0"
)

# Home Route
app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "HireLens API is running"}