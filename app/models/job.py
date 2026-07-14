from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class Job(Base):
    __tablename__ = "jobs"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key -> User Table
    recruiter_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Job Details
    title = Column(String(255), nullable=False)

    description_text = Column(Text, nullable=False)

    required_skills = Column(Text, nullable=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    recruiter = relationship("User", back_populates="jobs")

    #resumes = relationship(
     #   "Resume",
      #  back_populates="job",
      #  cascade="all, delete-orphan"
    #)