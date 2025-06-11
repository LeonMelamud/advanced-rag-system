"""
RAG Service Models for Chat Service
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SourceAttribution(BaseModel):
    """Source attribution for RAG responses"""

    document_id: UUID
    chunk_id: UUID
    collection_id: UUID
    filename: str
    chunk_text: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    chunk_sequence: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RetrievedChunk(BaseModel):
    """Retrieved chunk from vector database"""

    chunk_id: UUID
    document_id: UUID
    collection_id: UUID
    content: str
    embedding: Optional[List[float]] = None
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    rank: int


class ContextMergeResult(BaseModel):
    """Result of context merging operation"""

    merged_context: str
    selected_chunks: List[RetrievedChunk]
    total_tokens: int
    merge_strategy: str
    merge_metadata: Dict[str, Any] = Field(default_factory=dict)


class RAGRequest(BaseModel):
    """RAG processing request"""

    query: str = Field(..., min_length=1, max_length=10000)
    collection_ids: List[UUID] = Field(default_factory=list)
    top_k: int = Field(default=5, ge=1, le=50)
    context_settings: Dict[str, Any] = Field(default_factory=dict)
    user_id: UUID
    session_id: Optional[UUID] = None


class RAGResponse(BaseModel):
    """RAG processing response"""

    query: str
    response: str
    sources: List[SourceAttribution]
    context_used: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    processing_time_ms: int
    tokens_used: int
    model_used: str


class LLMRequest(BaseModel):
    """LLM generation request"""

    prompt: str
    context: str
    model: str = "gpt-4"
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, ge=1, le=4000)
    stream: bool = False


class LLMResponse(BaseModel):
    """LLM generation response"""

    content: str
    model: str
    tokens_used: int
    finish_reason: str
    response_time_ms: int


class EmbeddingRequest(BaseModel):
    """Embedding generation request"""

    text: str
    model: str = "text-embedding-3-small"


class EmbeddingResponse(BaseModel):
    """Embedding generation response"""

    embedding: List[float]
    model: str
    tokens_used: int


class VectorSearchRequest(BaseModel):
    """Vector database search request"""

    query_embedding: List[float]
    collection_ids: List[UUID]
    top_k: int = Field(default=10, ge=1, le=100)
    score_threshold: float = Field(default=0.0, ge=0.0, le=1.0)
    filters: Dict[str, Any] = Field(default_factory=dict)


class VectorSearchResponse(BaseModel):
    """Vector database search response"""

    chunks: List[RetrievedChunk]
    total_found: int
    search_time_ms: int


class StreamingChunk(BaseModel):
    """Streaming response chunk"""

    type: str  # "content", "source", "metadata", "error", "done"
    data: Any
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatStreamingResponse(BaseModel):
    """Complete streaming response metadata"""

    session_id: UUID
    message_id: UUID
    total_chunks: int
    total_tokens: int
    sources: List[SourceAttribution]
    metadata: Dict[str, Any] = Field(default_factory=dict)
