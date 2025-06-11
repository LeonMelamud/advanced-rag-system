"""
Vector Database Service
Provides a unified interface for vector operations using Qdrant
Follows DRY principles with shared functionality across services
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ResponseHandlingException
from qdrant_client.models import (
    CollectionInfo,
    CreateCollection,
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointsList,
    PointStruct,
    Record,
    SearchRequest,
    UpdateResult,
    VectorParams,
)

from ..config import DatabaseServiceConfig

logger = logging.getLogger(__name__)


class VectorPoint:
    """Represents a vector point with metadata"""

    def __init__(self, id: Union[str, UUID], vector: List[float], payload: Dict[str, Any] = None):
        self.id = str(id) if isinstance(id, UUID) else id
        self.vector = vector
        self.payload = payload or {}

    def to_qdrant_point(self) -> PointStruct:
        """Convert to Qdrant PointStruct"""
        return PointStruct(id=self.id, vector=self.vector, payload=self.payload)


class VectorSearchResult:
    """Represents a vector search result"""

    def __init__(
        self, id: str, score: float, payload: Dict[str, Any], vector: Optional[List[float]] = None
    ):
        self.id = id
        self.score = score
        self.payload = payload
        self.vector = vector

    @classmethod
    def from_qdrant_result(cls, result) -> "VectorSearchResult":
        """Create from Qdrant search result"""
        return cls(
            id=str(result.id),
            score=result.score,
            payload=result.payload or {},
            vector=getattr(result, "vector", None),
        )


class VectorService:
    """Service for vector database operations using Qdrant"""

    def __init__(self, config: DatabaseServiceConfig = None):
        self.config = config or DatabaseServiceConfig()
        self.client = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the vector service"""
        if self._initialized:
            return

        try:
            self.client = QdrantClient(
                host=self.config.qdrant_host,
                port=self.config.qdrant_port,
                timeout=self.config.qdrant_timeout,
            )

            # Test connection
            await self._test_connection()
            self._initialized = True
            logger.info("Vector service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize vector service: {e}")
            raise

    async def _test_connection(self) -> None:
        """Test Qdrant connection"""
        try:
            # Use asyncio to run sync method
            collections = await asyncio.get_event_loop().run_in_executor(
                None, self.client.get_collections
            )
            logger.info(f"Connected to Qdrant with {len(collections.collections)} collections")
        except Exception as e:
            raise ConnectionError(f"Cannot connect to Qdrant: {e}")

    async def ensure_collection(
        self, collection_name: str, vector_size: int = 1536, distance: Distance = Distance.COSINE
    ) -> bool:
        """Ensure collection exists, create if it doesn't"""
        if not self._initialized:
            await self.initialize()

        try:
            # Check if collection already exists
            collections = await asyncio.get_event_loop().run_in_executor(
                None, self.client.get_collections
            )

            existing_names = [col.name for col in collections.collections]

            if collection_name in existing_names:
                logger.debug(f"Collection '{collection_name}' already exists")
                return True

            # Create collection
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.client.create_collection,
                collection_name,
                VectorParams(size=vector_size, distance=distance),
            )

            logger.info(f"Created collection '{collection_name}' with vector size {vector_size}")
            return True

        except Exception as e:
            # Handle the case where collection was created between check and creation (race condition)
            if "already exists" in str(e):
                logger.debug(f"Collection '{collection_name}' was created by another process")
                return True

            logger.error(f"Failed to ensure collection '{collection_name}': {e}")
            raise

    async def upsert_points(self, collection_name: str, points: List[VectorPoint]) -> bool:
        """Insert or update vector points"""
        if not self._initialized:
            await self.initialize()

        if not points:
            return True

        try:
            qdrant_points = [point.to_qdrant_point() for point in points]

            result = await asyncio.get_event_loop().run_in_executor(
                None, self.client.upsert, collection_name, qdrant_points
            )

            logger.info(f"Upserted {len(points)} points to collection '{collection_name}'")
            return result.status == "completed"

        except Exception as e:
            logger.error(f"Failed to upsert points to '{collection_name}': {e}")
            raise

    async def search_vectors(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: float = 0.0,
        filters: Optional[Dict[str, Any]] = None,
        with_vectors: bool = False,
    ) -> List[VectorSearchResult]:
        """Search for similar vectors"""
        if not self._initialized:
            await self.initialize()

        try:
            # Build filter if provided
            qdrant_filter = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    if isinstance(value, list):
                        # Handle list values (e.g., collection_ids)
                        for v in value:
                            conditions.append(FieldCondition(key=key, match=MatchValue(value=v)))
                    else:
                        conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))

                if conditions:
                    qdrant_filter = Filter(must=conditions)

            # Perform search
            results = await asyncio.get_event_loop().run_in_executor(
                None,
                self.client.search,
                collection_name,
                query_vector,
                qdrant_filter,
                limit,
                with_vectors,
                score_threshold,
            )

            # Convert results
            search_results = [
                VectorSearchResult.from_qdrant_result(result)
                for result in results
                if result.score >= score_threshold
            ]

            logger.debug(f"Found {len(search_results)} vectors in '{collection_name}'")
            return search_results

        except Exception as e:
            logger.error(f"Failed to search vectors in '{collection_name}': {e}")
            raise

    async def get_point(
        self, collection_name: str, point_id: str, with_vector: bool = False
    ) -> Optional[VectorSearchResult]:
        """Get a specific point by ID"""
        if not self._initialized:
            await self.initialize()

        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, self.client.retrieve, collection_name, [point_id], with_vector
            )

            if not result:
                return None

            point = result[0]
            return VectorSearchResult(
                id=str(point.id),
                score=1.0,  # No score for direct retrieval
                payload=point.payload or {},
                vector=getattr(point, "vector", None) if with_vector else None,
            )

        except Exception as e:
            logger.error(f"Failed to get point '{point_id}' from '{collection_name}': {e}")
            return None

    async def delete_points(self, collection_name: str, point_ids: List[str]) -> bool:
        """Delete points by IDs"""
        if not self._initialized:
            await self.initialize()

        if not point_ids:
            return True

        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, self.client.delete, collection_name, point_ids
            )

            logger.info(f"Deleted {len(point_ids)} points from collection '{collection_name}'")
            return result.status == "completed"

        except Exception as e:
            logger.error(f"Failed to delete points from '{collection_name}': {e}")
            raise

    async def delete_collection(self, collection_name: str) -> bool:
        """Delete an entire collection"""
        if not self._initialized:
            await self.initialize()

        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, self.client.delete_collection, collection_name
            )

            logger.info(f"Deleted collection '{collection_name}'")
            return True

        except Exception as e:
            logger.error(f"Failed to delete collection '{collection_name}': {e}")
            raise

    async def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """Get collection information"""
        if not self._initialized:
            await self.initialize()

        try:
            info = await asyncio.get_event_loop().run_in_executor(
                None, self.client.get_collection, collection_name
            )

            return {
                "name": collection_name,
                "vectors_count": info.vectors_count,
                "indexed_vectors_count": info.indexed_vectors_count,
                "points_count": info.points_count,
                "segments_count": info.segments_count,
                "config": {
                    "params": {
                        "vector_size": info.config.params.vectors.size,
                        "distance": info.config.params.vectors.distance.value,
                    }
                },
            }

        except Exception as e:
            logger.error(f"Failed to get collection info for '{collection_name}': {e}")
            return None

    async def list_collections(self) -> List[str]:
        """List all collections"""
        if not self._initialized:
            await self.initialize()

        try:
            collections = await asyncio.get_event_loop().run_in_executor(
                None, self.client.get_collections
            )
            return [col.name for col in collections.collections]

        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return []

    async def count_points(
        self, collection_name: str, filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count points in collection with optional filters"""
        if not self._initialized:
            await self.initialize()

        try:
            # Build filter if provided
            qdrant_filter = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
                if conditions:
                    qdrant_filter = Filter(must=conditions)

            result = await asyncio.get_event_loop().run_in_executor(
                None, self.client.count, collection_name, qdrant_filter
            )

            return result.count

        except Exception as e:
            logger.error(f"Failed to count points in '{collection_name}': {e}")
            return 0

    async def close(self) -> None:
        """Close the vector service"""
        if self.client:
            # Qdrant client doesn't need explicit closing
            self.client = None
        self._initialized = False
        logger.info("Vector service closed")


# Singleton instance for shared use
_vector_service_instance = None


async def get_vector_service(config: DatabaseServiceConfig = None) -> VectorService:
    """Get shared vector service instance"""
    global _vector_service_instance

    if _vector_service_instance is None:
        _vector_service_instance = VectorService(config)
        await _vector_service_instance.initialize()

    return _vector_service_instance


async def close_vector_service() -> None:
    """Close shared vector service instance"""
    global _vector_service_instance

    if _vector_service_instance:
        await _vector_service_instance.close()
        _vector_service_instance = None
