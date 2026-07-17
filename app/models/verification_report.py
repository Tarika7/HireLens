from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    ForeignKey,
    JSON,
    DateTime,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class VerificationReport(Base):

    __tablename__ = "verification_reports"

    id = Column(Integer, primary_key=True, index=True)

    resume_id = Column(
        Integer,
        ForeignKey("resumes.id"),
        nullable=False
    )

    verification_type = Column(
        String(50),
        nullable=False
    )
    # github / linkedin / certificate

    status = Column(
        String(30),
        nullable=False
    )
    # verified / failed / not_submitted

    score = Column(
        Float,
        nullable=True
    )

    details = Column(
        JSON,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    resume = relationship(
        "Resume",
        back_populates="verification_reports"
    )