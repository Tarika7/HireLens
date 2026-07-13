from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.database.database import Base


class User(Base):
    """
    Represents a recruiter account.
    """

    __tablename__ = "users"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Recruiter Details
    full_name = Column(String(100), nullable=False)

    email = Column(String(255), unique=True, nullable=False, index=True)

    password = Column(String(255), nullable=False)

    role = Column(String(20), default="recruiter")

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())