from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class ParsedResume(Base):

    __tablename__ = "parsed_resumes"

    id = Column(Integer, primary_key=True, index=True)

    resume_id = Column(
        Integer,
        ForeignKey("resumes.id"),
        unique=True,
        nullable=False
    )

    candidate_name = Column(String)

    candidate_email = Column(String)

    candidate_phone = Column(String)

    technical_skills = Column(Text)

    soft_skills = Column(Text)

    education = Column(Text)

    experience_text = Column(Text)

    projects = Column(Text)

    certifications_claimed = Column(Text)

    resume = relationship(
        "Resume",
        back_populates="parsed_resume"
    )