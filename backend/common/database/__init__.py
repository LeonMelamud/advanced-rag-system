"""Database package for Advanced RAG System"""

from .base import Base, get_async_session, get_database_engine, get_db, get_db_session
from .models import *
from .redis import (
    CacheManager,
    EmbeddingCache,
    QueryCache,
    RateLimiter,
    SessionManager,
    get_cache_manager,
    get_rate_limiter,
    get_redis,
    get_session_manager,
    redis_manager,
)

# Optional vector database imports (only if qdrant-client is available)
try:
    from .vector import (
        VectorPoint,
        VectorSearchResult,
        VectorService,
        close_vector_service,
        get_vector_service,
    )

    _vector_available = True
except ImportError:
    # Vector database functionality not available
    VectorService = None
    VectorPoint = None
    VectorSearchResult = None
    get_vector_service = None
    close_vector_service = None
    _vector_available = False

__all__ = [
    "Base",
    "get_async_session",
    "get_database_engine",
    "get_db",
    "get_db_session",
    "get_redis",
    "get_cache_manager",
    "get_session_manager",
    "get_rate_limiter",
    "CacheManager",
    "SessionManager",
    "RateLimiter",
    "QueryCache",
    "EmbeddingCache",
    "redis_manager",
]

# Add vector exports only if available
if _vector_available:
    __all__.extend(
        [
            "VectorService",
            "VectorPoint",
            "VectorSearchResult",
            "get_vector_service",
            "close_vector_service",
        ]
    )
