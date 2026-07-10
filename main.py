from fastapi import FastAPI

# Create the FastAPI application
app = FastAPI(
    title="HireLens",
    description="AI-Powered Resume Verification & Recruitment Platform",
    version="1.0.0"
)

# Home Route
@app.get("/")
def home():
    return {
        "message": "Welcome to HireLens!",
        "status": "Application is running successfully."
    }