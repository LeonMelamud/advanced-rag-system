"""
Vector Integration Service for File Service
Handles storing and retrieving embeddings in Qdrant vector database
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from backend.common.database.models import DocumentChunk
from backend.common.database.vector import (
    VectorPoint,
    VectorSearchResult,
    VectorService,
    get_vector_service,
)

from ..core.config import get_settings

logger = logging.getLogger(__name__)


class FileVectorService:
    """Service for managing file chunk vectors in Qdrant"""

    def __init__(self):
        self.settings = get_settings()
        self.vector_service: Optional[VectorService] = None

    async def initialize(self) -> None:
        """Initialize the vector service"""
        if self.vector_service is None:
            self.vector_service = await get_vector_service(self.settings)
            logger.info("File vector service initialized")

    async def get_collection_name(self, collection_id: str) -> str:
        """Get Qdrant collection name for a collection"""
        # Use the collection_id directly to match existing collections
        return collection_id

    async def ensure_collection_exists(self, collection_id: str, vector_size: int = 1536) -> bool:
        """Ensure Qdrant collection exists for the given collection"""
        if not self.vector_service:
            await self.initialize()

        collection_name = await self.get_collection_name(collection_id)
        return await self.vector_service.ensure_collection(
            collection_name=collection_name, vector_size=vector_size
        )

    async def store_chunk_embeddings(
        self, chunks: List[DocumentChunk], embeddings: List[List[float]], collection_id: str
    ) -> List[str]:
        """Store chunk embeddings in Qdrant"""
        if not self.vector_service:
            await self.initialize()

        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")

        # Ensure collection exists
        await self.ensure_collection_exists(collection_id, len(embeddings[0]))

        collection_name = await self.get_collection_name(collection_id)

        # Create vector points
        vector_points = []
        vector_ids = []

        for chunk, embedding in zip(chunks, embeddings):
            vector_id = str(chunk.id)
            vector_ids.append(vector_id)

            # Create payload with chunk metadata
            payload = {
                "chunk_id": str(chunk.id),
                "file_id": str(chunk.file_id),
                "collection_id": collection_id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "content_length": chunk.content_length,
                "embedding_model": chunk.embedding_model,
                "page_number": chunk.page_number,
                "section_title": chunk.section_title,
                "chunk_metadata": chunk.chunk_metadata or {},
            }

            vector_point = VectorPoint(id=vector_id, vector=embedding, payload=payload)
            vector_points.append(vector_point)

        # Store in Qdrant
        success = await self.vector_service.upsert_points(
            collection_name=collection_name, points=vector_points
        )

        if success:
            logger.info(f"Stored {len(vector_points)} embeddings in collection '{collection_name}'")
            return vector_ids
        else:
            raise RuntimeError("Failed to store embeddings in Qdrant")

    async def search_similar_chunks(
        self,
        query_embedding: List[float],
        collection_id: str,
        limit: int = 10,
        score_threshold: float = 0.0,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[VectorSearchResult]:
        """Search for similar chunks in a collection"""
        if not self.vector_service:
            await self.initialize()

        collection_name = await self.get_collection_name(collection_id)

        # Add collection_id to filters
        search_filters = {"collection_id": collection_id}
        if filters:
            search_filters.update(filters)

        results = await self.vector_service.search_vectors(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=limit,
            score_threshold=score_threshold,
            filters=search_filters,
        )

        logger.debug(f"Found {len(results)} similar chunks in collection '{collection_id}'")
        return results

    async def search_across_collections(
        self,
        query_embedding: List[float],
        collection_ids: List[str],
        limit: int = 10,
        score_threshold: float = 0.0,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[VectorSearchResult]:
        """Search for similar chunks across multiple collections"""
        if not self.vector_service:
            await self.initialize()

        all_results = []

        # Search each collection
        for collection_id in collection_ids:
            try:
                results = await self.search_similar_chunks(
                    query_embedding=query_embedding,
                    collection_id=collection_id,
                    limit=limit,
                    score_threshold=score_threshold,
                    filters=filters,
                )
                all_results.extend(results)
            except Exception as e:
                logger.warning(f"Failed to search collection '{collection_id}': {e}")
                continue

        # Sort by score and limit results
        all_results.sort(key=lambda x: x.score, reverse=True)
        return all_results[:limit]

    async def get_chunk_by_vector_id(
        self, vector_id: str, collection_id: str
    ) -> Optional[VectorSearchResult]:
        """Get a specific chunk by its vector ID"""
        if not self.vector_service:
            await self.initialize()

        collection_name = await self.get_collection_name(collection_id)

        result = await self.vector_service.get_point(
            collection_name=collection_name, point_id=vector_id, with_vector=True
        )

        return result

    async def delete_chunk_embeddings(self, chunk_ids: List[str], collection_id: str) -> bool:
        """Delete chunk embeddings from Qdrant"""
        if not self.vector_service:
            await self.initialize()

        collection_name = await self.get_collection_name(collection_id)

        # Convert chunk IDs to vector IDs
        vector_ids = [str(chunk_id) for chunk_id in chunk_ids]  # Use UUID directly

        success = await self.vector_service.delete_points(
            collection_name=collection_name, point_ids=vector_ids
        )

        if success:
            logger.info(f"Deleted {len(vector_ids)} embeddings from collection '{collection_name}'")

        return success

    async def delete_file_embeddings(self, file_id: str, collection_id: str) -> bool:
        """Delete all embeddings for a specific file"""
        if not self.vector_service:
            await self.initialize()

        collection_name = await self.get_collection_name(collection_id)

        # Search for all chunks from this file
        results = await self.vector_service.search_vectors(
            collection_name=collection_name,
            query_vector=[0.0] * 1536,  # Dummy vector for filter-only search
            limit=10000,  # Large limit to get all chunks
            filters={"file_id": file_id},
        )

        if not results:
            return True

        # Extract vector IDs
        vector_ids = [result.id for result in results]

        # Delete the points
        return await self.vector_service.delete_points(
            collection_name=collection_name, point_ids=vector_ids
        )

    async def get_collection_stats(self, collection_id: str) -> Dict[str, Any]:
        """Get statistics for a collection"""
        if not self.vector_service:
            await self.initialize()

        collection_name = await self.get_collection_name(collection_id)

        # Get collection info
        info = await self.vector_service.get_collection_info(collection_name)
        if not info:
            return {"exists": False}

        # Count points for this collection
        point_count = await self.vector_service.count_points(
            collection_name=collection_name, filters={"collection_id": collection_id}
        )

        return {
            "exists": True,
            "collection_name": collection_name,
            "total_points": info["points_count"],
            "collection_points": point_count,
            "vector_size": info["config"]["params"]["vector_size"],
            "distance_metric": info["config"]["params"]["distance"],
        }

    async def list_collections(self) -> List[str]:
        """List all Qdrant collections"""
        if not self.vector_service:
            await self.initialize()

        return await self.vector_service.list_collections()


# Singleton instance
_file_vector_service = None


async def get_file_vector_service() -> FileVectorService:
    """Get shared file vector service instance"""
    global _file_vector_service

    if _file_vector_service is None:
        _file_vector_service = FileVectorService()
        await _file_vector_service.initialize()

    return _file_vector_service
