"""
Shared Pydantic schemas for the Advanced RAG System.

These schemas define the data models used for API communication
between services and for data validation.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )


class FileType(str, Enum):
    """Supported file types for ingestion."""

    PDF = "pdf"
    CSV = "csv"
    TXT = "txt"
    AUDIO = "audio"


class ProcessingStatus(str, Enum):
    """File processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class ChunkingStrategy(str, Enum):
    """Available chunking strategies."""

    FIXED_SIZE = "fixed_size"
    RECURSIVE = "recursive"
    SEMANTIC = "semantic"
    DOCUMENT_SPECIFIC = "document_specific"


class EmbeddingModel(str, Enum):
    """Supported embedding models."""

    OPENAI_ADA_002 = "text-embedding-ada-002"
    OPENAI_3_SMALL = "text-embedding-3-small"
    OPENAI_3_LARGE = "text-embedding-3-large"
    GEMINI_EMBEDDING_001 = "gemini-embedding-001"
    SENTENCE_TRANSFORMERS = "sentence-transformers"


class LLMModel(str, Enum):
    """Supported LLM models."""

    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GEMINI_PRO = "gemini-pro"
    GEMINI_PRO_VISION = "gemini-pro-vision"
    CLAUDE_3_OPUS = "claude-3-opus"
    CLAUDE_3_SONNET = "claude-3-sonnet"


# File-related schemas
class FileMetadata(BaseSchema):
    """File metadata schema."""

    filename: str
    file_size: int
    mime_type: str
    checksum: str
    upload_timestamp: datetime
    file_type: FileType
    extracted_metadata: Optional[Dict[str, Any]] = None


class FileUploadRequest(BaseSchema):
    """File upload request schema."""

    collection_ids: List[UUID] = Field(default_factory=list)
    user_metadata: Optional[Dict[str, Any]] = None
    processing_options: Optional[Dict[str, Any]] = None


class FileUploadResponse(BaseSchema):
    """File upload response schema."""

    file_id: UUID
    filename: str
    status: ProcessingStatus
    message: str


# Collection-related schemas
class CollectionConfig(BaseSchema):
    """Knowledge collection configuration."""

    name: str
    description: Optional[str] = None
    system_prompt: str
    llm_model: LLMModel
    embedding_model: EmbeddingModel
    chunking_strategy: ChunkingStrategy
    chunking_params: Dict[str, Any] = Field(default_factory=dict)
    tool_configs: Optional[Dict[str, Any]] = None


class CollectionCreate(BaseSchema):
    """Schema for creating a new collection."""

    config: CollectionConfig
    is_public: bool = False
    tags: List[str] = Field(default_factory=list)


class CollectionUpdate(BaseSchema):
    """Schema for updating a collection."""

    config: Optional[CollectionConfig] = None
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = None


class Collection(BaseSchema):
    """Complete collection schema."""

    id: UUID
    config: CollectionConfig
    is_public: bool
    tags: List[str]
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
    version: int
    document_count: int = 0


# Chat-related schemas
class ChatMessage(BaseSchema):
    """Chat message schema."""

    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class ChatSession(BaseSchema):
    """Chat session schema."""

    id: UUID
    user_id: UUID
    collection_ids: List[UUID]
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime
    is_active: bool = True


class ChatRequest(BaseSchema):
    """Chat request schema."""

    message: str
    session_id: Optional[UUID] = None
    collection_ids: List[UUID]
    stream: bool = True
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None


class ChatResponse(BaseSchema):
    """Chat response schema."""

    session_id: UUID
    message: str
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime


# Retrieval-related schemas
class DocumentChunk(BaseSchema):
    """Document chunk schema."""

    id: UUID
    document_id: UUID
    collection_id: UUID
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    chunk_index: int
    token_count: int


class RetrievalRequest(BaseSchema):
    """Retrieval request schema."""

    query: str
    collection_ids: List[UUID]
    top_k: int = 10
    filters: Optional[Dict[str, Any]] = None
    rerank: bool = True


class RetrievalResult(BaseSchema):
    """Retrieval result schema."""

    chunks: List[DocumentChunk]
    scores: List[float]
    total_found: int
    query_metadata: Dict[str, Any] = Field(default_factory=dict)


# User and authentication schemas
class UserRole(str, Enum):
    """User roles."""

    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class User(BaseSchema):
    """User schema."""

    id: UUID
    email: str
    username: str
    role: UserRole
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class TokenData(BaseSchema):
    """JWT token data schema."""

    user_id: UUID
    username: str
    role: UserRole
    exp: datetime


# Error schemas
class ErrorDetail(BaseSchema):
    """Error detail schema."""

    code: str
    message: str
    field: Optional[str] = None


class ErrorResponse(BaseSchema):
    """Error response schema."""

    error: str
    details: List[ErrorDetail] = Field(default_factory=list)
    timestamp: datetime
    request_id: Optional[str] = None


# Health check schemas
class HealthStatus(str, Enum):
    """Health check status."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


class ServiceHealth(BaseSchema):
    """Service health schema."""

    service: str
    status: HealthStatus
    version: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None


class SystemHealth(BaseSchema):
    """System health schema."""

    status: HealthStatus
    services: List[ServiceHealth]
    timestamp: datetime
