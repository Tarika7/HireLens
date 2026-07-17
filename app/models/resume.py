from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class Resume(Base):

    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)

    recruiter_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    job_id = Column(
        Integer,
        ForeignKey("jobs.id"),
        nullable=False
    )

    original_filename = Column(
        String,
        nullable=False
    )

    stored_filename = Column(
        String,
        nullable=False
    )

    file_path = Column(
        String,
        nullable=False
    )

    # ⭐ NEW
    raw_text = Column(
        Text,
        nullable=True
    )

    parsing_status = Column(
        String,
        default="Pending"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    recruiter = relationship(
        "User",
        back_populates="resumes"
    )

    job = relationship(
        "Job",
        back_populates="resumes"
    )

    parsed_resume = relationship(
        "ParsedResume",
        back_populates="resume",
        uselist=False,
        cascade="all, delete-orphan"
    )

    matching_result = relationship(
        "MatchingResult",
        back_populates="resume",
        uselist=False,
        cascade="all, delete-orphan"
    )
    verification_reports = relationship(
    "VerificationReport",
    back_populates="resume",
    cascade="all, delete-orphan"
)