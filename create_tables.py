from app.database.database import Base, engine

# Import ALL models
from app.models.user import User
from app.models.job import Job
from app.models.resume import Resume
from app.models.parsed_resume import ParsedResume

print("Creating database tables...")

Base.metadata.create_all(bind=engine)

print("✅ Tables created successfully!")