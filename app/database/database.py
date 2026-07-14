from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config.settings import (
    DB_USER,
    DB_PASSWORD,
    DB_HOST,
    DB_PORT,
    DB_NAME,
)

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
)

# Create database engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all database models
Base = declarative_base()

def get_db():
    """
    Creates a new database session for every request.
    Automatically closes it after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all database tables
def create_tables():
    Base.metadata.create_all(bind=engine)