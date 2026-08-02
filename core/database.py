"""
core/database.py

Database configuration for the YouTube Downloader application.

Creates:
- SQLAlchemy Engine
- Session Factory
- Declarative Base
- Database initialization
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from core.config import settings
from core.logger import app_logger

# ==========================================================
# Database Configuration
# ==========================================================

DATABASE_PATH = settings.DATA_DIR / settings.DATABASE_FILE
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


# ==========================================================
# Base Model
# ==========================================================

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    """
    pass


# ==========================================================
# Database Engine
# ==========================================================

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args={
        "check_same_thread": False
    },
)


# ==========================================================
# Session Factory
# ==========================================================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


# ==========================================================
# FastAPI Dependency
# ==========================================================

def get_db() -> Generator[Session, None, None]:
    """
    Returns a database session.

    Example:

        @router.get("/")
        def home(db: Session = Depends(get_db)):
            ...

    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ==========================================================
# Database Initialization
# ==========================================================

def create_database() -> None:
    """
    Import all SQLAlchemy models and create database tables.
    """

    # Import models so SQLAlchemy registers them
    import models

    Base.metadata.create_all(bind=engine)

    app_logger.info(f"Database initialized: {DATABASE_PATH}")