"""
RAG Service for Chat Service
Handles embedding generation, vector search, context merging, and LLM response generation
"""

import asyncio
import logging
import time
from typing import Any, AsyncGenerator, Dict, List, Optional
from uuid import UUID

import httpx
import openai
from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchValue

from ..core.config import get_settings
from ..models.rag import (
    ContextMergeResult,
    EmbeddingRequest,
    EmbeddingResponse,
    LLMRequest,
    LLMResponse,
    RAGRequest,
    RAGResponse,
    RetrievedChunk,
    SourceAttribution,
    StreamingChunk,
    VectorSearchRequest,
    VectorSearchResponse,
)

logger = logging.getLogger(__name__)


class RAGService:
    """RAG service for processing queries and generating responses"""

    def __init__(self):
        self.settings = get_settings()
        self.openai_client = openai.AsyncOpenAI(api_key=self.settings.openai_api_key)
        self.qdrant_client = QdrantClient(
            host=self.settings.qdrant_host, port=self.settings.qdrant_port
        )

    async def process_rag_request(self, request: RAGRequest) -> RAGResponse:
        """Process a complete RAG request"""
        start_time = time.time()

        try:
            logger.info(f"Processing RAG request for user {request.user_id}")

            # Step 1: Generate query embedding
            embedding_response = await self.generate_embedding(
                EmbeddingRequest(text=request.query, model=self.settings.default_embedding_model)
            )

            # Step 2: Search vector database
            search_request = VectorSearchRequest(
                query_embedding=embedding_response.embedding,
                collection_ids=request.collection_ids,
                top_k=request.top_k * 2,  # Get more for better merging
                score_threshold=0.3,
            )
            search_response = await self.vector_search(search_request)

            # Step 3: Merge and rank contexts
            merge_result = await self.merge_contexts(
                search_response.chunks, request.query, max_tokens=self.settings.max_context_tokens
            )

            # Step 4: Generate LLM response
            llm_request = LLMRequest(
                prompt=self._build_prompt(request.query, merge_result.merged_context),
                context=merge_result.merged_context,
                model=self.settings.default_model,
                temperature=0.1,
                max_tokens=1000,
            )
            llm_response = await self.generate_llm_response(llm_request)

            # Step 5: Extract source attribution
            sources = self._extract_source_attribution(merge_result.selected_chunks)

            processing_time = int((time.time() - start_time) * 1000)

            return RAGResponse(
                query=request.query,
                response=llm_response.content,
                sources=sources,
                context_used=merge_result.merged_context,
                metadata={
                    "chunks_retrieved": len(search_response.chunks),
                    "chunks_used": len(merge_result.selected_chunks),
                    "merge_strategy": merge_result.merge_strategy,
                    "embedding_model": self.settings.default_embedding_model,
                    "llm_model": llm_response.model,
                },
                processing_time_ms=processing_time,
                tokens_used=llm_response.tokens_used,
                model_used=llm_response.model,
            )

        except Exception as e:
            logger.error(f"Error processing RAG request: {e}", exc_info=True)
            raise

    async def process_streaming_rag_request(
        self, request: RAGRequest
    ) -> AsyncGenerator[StreamingChunk, None]:
        """Process RAG request with streaming response"""
        try:
            logger.info(f"Processing streaming RAG request for user {request.user_id}")

            # Step 1: Generate embedding and search (non-streaming)
            yield StreamingChunk(type="status", data={"status": "generating_embedding"})

            embedding_response = await self.generate_embedding(EmbeddingRequest(text=request.query))

            yield StreamingChunk(type="status", data={"status": "searching_vectors"})

            search_request = VectorSearchRequest(
                query_embedding=embedding_response.embedding,
                collection_ids=request.collection_ids,
                top_k=request.top_k * 2,
            )
            search_response = await self.vector_search(search_request)

            yield StreamingChunk(type="status", data={"status": "merging_context"})

            merge_result = await self.merge_contexts(
                search_response.chunks, request.query, max_tokens=self.settings.max_context_tokens
            )

            # Send source information
            sources = self._extract_source_attribution(merge_result.selected_chunks)
            for source in sources:
                yield StreamingChunk(type="source", data=source.dict())

            yield StreamingChunk(type="status", data={"status": "generating_response"})

            # Step 2: Stream LLM response
            llm_request = LLMRequest(
                prompt=self._build_prompt(request.query, merge_result.merged_context),
                context=merge_result.merged_context,
                model=self.settings.default_model,
                stream=True,
            )

            async for chunk in self.stream_llm_response(llm_request):
                yield StreamingChunk(type="content", data=chunk)

            # Send completion metadata
            yield StreamingChunk(
                type="metadata",
                data={
                    "chunks_retrieved": len(search_response.chunks),
                    "chunks_used": len(merge_result.selected_chunks),
                    "sources_count": len(sources),
                },
            )

            yield StreamingChunk(type="done", data={"status": "completed"})

        except Exception as e:
            logger.error(f"Error in streaming RAG: {e}", exc_info=True)
            yield StreamingChunk(type="error", data={"error": str(e), "status": "failed"})

    async def generate_embedding(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate text embedding"""
        try:
            response = await self.openai_client.embeddings.create(
                input=request.text, model=request.model
            )

            return EmbeddingResponse(
                embedding=response.data[0].embedding,
                model=response.model,
                tokens_used=response.usage.total_tokens,
            )

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    async def vector_search(self, request: VectorSearchRequest) -> VectorSearchResponse:
        """Search vector database"""
        start_time = time.time()

        try:
            all_chunks = []

            # Search each collection
            for collection_id in request.collection_ids:
                collection_name = f"knowledge_collection_{collection_id}"

                # Build filter if needed
                search_filter = None
                if request.filters:
                    conditions = []
                    for key, value in request.filters.items():
                        conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
                    search_filter = Filter(must=conditions)

                # Perform search
                search_results = self.qdrant_client.search(
                    collection_name=collection_name,
                    query_vector=request.query_embedding,
                    limit=request.top_k,
                    score_threshold=request.score_threshold,
                    query_filter=search_filter,
                    with_payload=True,
                )

                # Convert to RetrievedChunk objects
                for i, result in enumerate(search_results):
                    chunk = RetrievedChunk(
                        chunk_id=UUID(result.payload["chunk_id"]),
                        document_id=UUID(result.payload["document_id"]),
                        collection_id=collection_id,
                        content=result.payload["chunk_text"],
                        similarity_score=result.score,
                        metadata=result.payload.get("metadata", {}),
                        rank=i + 1,
                    )
                    all_chunks.append(chunk)

            search_time = int((time.time() - start_time) * 1000)

            return VectorSearchResponse(
                chunks=all_chunks, total_found=len(all_chunks), search_time_ms=search_time
            )

        except Exception as e:
            logger.error(f"Error in vector search: {e}")
            raise

    async def merge_contexts(
        self, chunks: List[RetrievedChunk], query: str, max_tokens: int = 4000
    ) -> ContextMergeResult:
        """Merge and rank contexts using Enhanced RRF"""
        try:
            # Implement Enhanced RRF algorithm
            rrf_k = self.settings.rrf_k

            # Group chunks by collection for RRF
            collection_chunks = {}
            for chunk in chunks:
                if chunk.collection_id not in collection_chunks:
                    collection_chunks[chunk.collection_id] = []
                collection_chunks[chunk.collection_id].append(chunk)

            # Calculate RRF scores
            rrf_scores = {}
            for collection_id, collection_chunks_list in collection_chunks.items():
                # Sort by similarity score
                sorted_chunks = sorted(
                    collection_chunks_list, key=lambda x: x.similarity_score, reverse=True
                )

                for rank, chunk in enumerate(sorted_chunks, 1):
                    chunk_key = str(chunk.chunk_id)
                    if chunk_key not in rrf_scores:
                        rrf_scores[chunk_key] = {"chunk": chunk, "score": 0.0}

                    # RRF formula: 1 / (k + rank)
                    rrf_scores[chunk_key]["score"] += 1.0 / (rrf_k + rank)

            # Sort by RRF score
            sorted_chunks = sorted(rrf_scores.values(), key=lambda x: x["score"], reverse=True)

            # Select chunks within token limit
            selected_chunks = []
            total_tokens = 0

            for item in sorted_chunks:
                chunk = item["chunk"]
                chunk_tokens = len(chunk.content) // 4  # Rough token estimation

                if total_tokens + chunk_tokens <= max_tokens:
                    selected_chunks.append(chunk)
                    total_tokens += chunk_tokens
                else:
                    break

            # Build merged context
            context_parts = []
            for i, chunk in enumerate(selected_chunks, 1):
                context_parts.append(f"[Source {i}] {chunk.content}")

            merged_context = "\n\n".join(context_parts)

            return ContextMergeResult(
                merged_context=merged_context,
                selected_chunks=selected_chunks,
                total_tokens=total_tokens,
                merge_strategy="enhanced_rrf",
                merge_metadata={
                    "rrf_k": rrf_k,
                    "collections_searched": len(collection_chunks),
                    "total_chunks_available": len(chunks),
                },
            )

        except Exception as e:
            logger.error(f"Error merging contexts: {e}")
            raise

    async def generate_llm_response(self, request: LLMRequest) -> LLMResponse:
        """Generate LLM response"""
        start_time = time.time()

        try:
            response = await self.openai_client.chat.completions.create(
                model=request.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant that answers questions based on the provided context. Always cite your sources.",
                    },
                    {"role": "user", "content": request.prompt},
                ],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )

            response_time = int((time.time() - start_time) * 1000)

            return LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                tokens_used=response.usage.total_tokens,
                finish_reason=response.choices[0].finish_reason,
                response_time_ms=response_time,
            )

        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            raise

    async def stream_llm_response(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Stream LLM response"""
        try:
            stream = await self.openai_client.chat.completions.create(
                model=request.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant that answers questions based on the provided context. Always cite your sources.",
                    },
                    {"role": "user", "content": request.prompt},
                ],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Error streaming LLM response: {e}")
            raise

    def _build_prompt(self, query: str, context: str) -> str:
        """Build prompt for LLM"""
        return f"""Based on the following context, please answer the user's question. If the context doesn't contain enough information to answer the question, say so clearly.

Context:
{context}

Question: {query}

Please provide a comprehensive answer based on the context above, and cite the relevant sources using [Source X] notation."""

    def _extract_source_attribution(self, chunks: List[RetrievedChunk]) -> List[SourceAttribution]:
        """Extract source attribution from chunks"""
        sources = []

        for i, chunk in enumerate(chunks, 1):
            source = SourceAttribution(
                document_id=chunk.document_id,
                chunk_id=chunk.chunk_id,
                collection_id=chunk.collection_id,
                filename=chunk.metadata.get("filename", "Unknown"),
                chunk_text=(
                    chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content
                ),
                relevance_score=chunk.similarity_score,
                chunk_sequence=chunk.rank,
                metadata=chunk.metadata,
            )
            sources.append(source)

        return sources
