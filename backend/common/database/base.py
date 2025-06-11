"""Database base configuration for Advanced RAG System"""

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool

# Create the declarative base
Base = declarative_base()

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://rag_user:rag_password@localhost:5433/advanced_rag"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    poolclass=NullPool,  # Use NullPool for async
    future=True,
)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_db_session():
    """Get database session context manager for background tasks"""
    return AsyncSessionLocal()


# Alias for compatibility
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session (alias for get_async_session)"""
    async for session in get_async_session():
        yield session


def get_database_engine():
    """Get the database engine"""
    return engine
