"""
Shared Database Session Management
Database utilities following DRY principles
"""

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://rag_user:rag_password@localhost:5433/rag_database"
)

# Create engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models (imported from models.py to maintain consistency)
from backend.common.models import Base


def get_database_session() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI
    Following DRY principles for session management
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables (use with caution)"""
    Base.metadata.drop_all(bind=engine)
