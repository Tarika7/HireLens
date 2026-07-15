from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    ForeignKey,
    JSON,
    DateTime
)

from sqlalchemy.sql import func

from sqlalchemy.orm import relationship

from app.database.database import Base


class MatchingResult(Base):

    __tablename__ = "matching_results"

    id = Column(Integer, primary_key=True, index=True)

    resume_id = Column(
        Integer,
        ForeignKey("resumes.id"),
        nullable=False
    )

    job_id = Column(
        Integer,
        ForeignKey("jobs.id"),
        nullable=False
    )

    # ----------------------------
    # Module 4
    # ----------------------------

    match_score = Column(
        Float,
        nullable=False
    )

    match_reasons = Column(
        JSON,
        nullable=False
    )

    # ----------------------------
    # Module 5+
    # ----------------------------

    confidence_score = Column(
        Float,
        nullable=True
    )

    evidence_coverage = Column(
        Float,
        nullable=True
    )

    recommendation = Column(
        String(100),
        nullable=True
    )

    confidence_reasons = Column(
        JSON,
        nullable=True
    )
    created_at = Column(
    DateTime(timezone=True),
    server_default=func.now()
)

    resume = relationship(
        "Resume",
        back_populates="matching_result"
    )

    job = relationship(
        "Job",
        back_populates="matching_results"
    )