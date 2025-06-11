"""Redis integration for Advanced RAG System"""

import json
import logging
import os
from datetime import timedelta
from typing import Any, Dict, Optional, Union

import redis.asyncio as redis
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class RedisManager:
    """Redis connection and operation manager"""

    def __init__(self):
        self.redis: Optional[Redis] = None
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6380")

    async def connect(self) -> Redis:
        """Establish Redis connection"""
        if self.redis is None:
            try:
                self.redis = redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    retry_on_timeout=True,
                    socket_keepalive=True,
                    socket_keepalive_options={},
                    health_check_interval=30,
                )
                # Test connection
                await self.redis.ping()
                logger.info("Redis connection established successfully")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise
        return self.redis

    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.aclose()
            self.redis = None
            logger.info("Redis connection closed")

    async def get_redis(self) -> Redis:
        """Get Redis connection, creating if needed"""
        if self.redis is None:
            await self.connect()
        return self.redis


# Global Redis manager instance
redis_manager = RedisManager()


async def get_redis() -> Redis:
    """Dependency to get Redis connection"""
    return await redis_manager.get_redis()


class CacheManager:
    """High-level caching operations"""

    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = await self.redis.get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[Union[int, timedelta]] = None) -> bool:
        """Set value in cache with optional TTL"""
        try:
            serialized_value = json.dumps(value, default=str)
            if ttl:
                if isinstance(ttl, timedelta):
                    ttl = int(ttl.total_seconds())
                return await self.redis.setex(key, ttl, serialized_value)
            else:
                return await self.redis.set(key, serialized_value)
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter"""
        try:
            return await self.redis.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return None

    async def expire(self, key: str, ttl: Union[int, timedelta]) -> bool:
        """Set TTL for existing key"""
        try:
            if isinstance(ttl, timedelta):
                ttl = int(ttl.total_seconds())
            return await self.redis.expire(key, ttl)
        except Exception as e:
            logger.error(f"Cache expire error for key {key}: {e}")
            return False


class SessionManager:
    """Session management using Redis"""

    def __init__(self, redis: Redis, session_prefix: str = "session:"):
        self.redis = redis
        self.session_prefix = session_prefix
        self.default_ttl = timedelta(hours=24)  # 24 hour sessions

    def _session_key(self, session_id: str) -> str:
        """Generate session key"""
        return f"{self.session_prefix}{session_id}"

    async def create_session(
        self, session_id: str, data: Dict[str, Any], ttl: Optional[timedelta] = None
    ) -> bool:
        """Create new session"""
        try:
            key = self._session_key(session_id)
            serialized_data = json.dumps(data, default=str)
            ttl_seconds = int((ttl or self.default_ttl).total_seconds())
            return await self.redis.setex(key, ttl_seconds, serialized_data)
        except Exception as e:
            logger.error(f"Session create error for {session_id}: {e}")
            return False

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        try:
            key = self._session_key(session_id)
            data = await self.redis.get(key)
            if data is None:
                return None
            return json.loads(data)
        except Exception as e:
            logger.error(f"Session get error for {session_id}: {e}")
            return None

    async def update_session(
        self, session_id: str, data: Dict[str, Any], extend_ttl: bool = True
    ) -> bool:
        """Update session data"""
        try:
            key = self._session_key(session_id)
            serialized_data = json.dumps(data, default=str)

            if extend_ttl:
                ttl_seconds = int(self.default_ttl.total_seconds())
                return await self.redis.setex(key, ttl_seconds, serialized_data)
            else:
                return await self.redis.set(key, serialized_data, keepttl=True)
        except Exception as e:
            logger.error(f"Session update error for {session_id}: {e}")
            return False

    async def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        try:
            key = self._session_key(session_id)
            result = await self.redis.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Session delete error for {session_id}: {e}")
            return False

    async def extend_session(self, session_id: str, ttl: Optional[timedelta] = None) -> bool:
        """Extend session TTL"""
        try:
            key = self._session_key(session_id)
            ttl_seconds = int((ttl or self.default_ttl).total_seconds())
            return await self.redis.expire(key, ttl_seconds)
        except Exception as e:
            logger.error(f"Session extend error for {session_id}: {e}")
            return False

    async def session_exists(self, session_id: str) -> bool:
        """Check if session exists"""
        try:
            key = self._session_key(session_id)
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Session exists error for {session_id}: {e}")
            return False


class RateLimiter:
    """Rate limiting using Redis"""

    def __init__(self, redis: Redis, prefix: str = "rate_limit:"):
        self.redis = redis
        self.prefix = prefix

    def _rate_limit_key(self, identifier: str, window: str) -> str:
        """Generate rate limit key"""
        return f"{self.prefix}{identifier}:{window}"

    async def is_allowed(
        self, identifier: str, limit: int, window: timedelta, window_name: Optional[str] = None
    ) -> tuple[bool, int, int]:
        """
        Check if request is allowed under rate limit
        Returns: (is_allowed, current_count, remaining_count)
        """
        try:
            if window_name is None:
                window_name = str(int(window.total_seconds()))

            key = self._rate_limit_key(identifier, window_name)

            # Use pipeline for atomic operations
            async with self.redis.pipeline() as pipe:
                await pipe.incr(key)
                await pipe.expire(key, int(window.total_seconds()))
                results = await pipe.execute()

            current_count = results[0]
            is_allowed = current_count <= limit
            remaining = max(0, limit - current_count)

            return is_allowed, current_count, remaining

        except Exception as e:
            logger.error(f"Rate limit check error for {identifier}: {e}")
            # Fail open - allow request if Redis is down
            return True, 0, limit


async def get_cache_manager() -> CacheManager:
    """Dependency to get cache manager"""
    redis = await get_redis()
    return CacheManager(redis)


async def get_session_manager() -> SessionManager:
    """Dependency to get session manager"""
    redis = await get_redis()
    return SessionManager(redis)


async def get_rate_limiter() -> RateLimiter:
    """Dependency to get rate limiter"""
    redis = await get_redis()
    return RateLimiter(redis)


# Cache decorators and utilities
def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments"""
    key_parts = []
    for arg in args:
        key_parts.append(str(arg))
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}:{v}")
    return ":".join(key_parts)


# Common cache patterns
class QueryCache:
    """Specialized cache for query results"""

    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.prefix = "query:"
        self.default_ttl = timedelta(minutes=15)

    async def get_query_result(self, query_hash: str) -> Optional[Any]:
        """Get cached query result"""
        key = f"{self.prefix}{query_hash}"
        return await self.cache.get(key)

    async def cache_query_result(
        self, query_hash: str, result: Any, ttl: Optional[timedelta] = None
    ) -> bool:
        """Cache query result"""
        key = f"{self.prefix}{query_hash}"
        return await self.cache.set(key, result, ttl or self.default_ttl)


class EmbeddingCache:
    """Specialized cache for embeddings"""

    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.prefix = "embedding:"
        self.default_ttl = timedelta(hours=24)

    async def get_embedding(self, text_hash: str) -> Optional[list]:
        """Get cached embedding"""
        key = f"{self.prefix}{text_hash}"
        return await self.cache.get(key)

    async def cache_embedding(
        self, text_hash: str, embedding: list, ttl: Optional[timedelta] = None
    ) -> bool:
        """Cache embedding"""
        key = f"{self.prefix}{text_hash}"
        return await self.cache.set(key, embedding, ttl or self.default_ttl)
