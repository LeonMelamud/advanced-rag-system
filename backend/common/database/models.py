"""SQLAlchemy models for Advanced RAG System"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class UUIDMixin:
    """Mixin for UUID primary key"""

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)


# Auth Service Models
class User(Base, UUIDMixin, TimestampMixin):
    """User model for authentication"""

    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    collections = relationship("Collection", back_populates="owner")
    chat_sessions = relationship("ChatSession", back_populates="user")


class UserSession(Base, UUIDMixin, TimestampMixin):
    """User session model for JWT token management"""

    __tablename__ = "user_sessions"
    __table_args__ = {"schema": "auth"}

    user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id"), nullable=False)
    token_jti = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)

    # Relationships
    user = relationship("User")


# Collection Service Models
class CollectionStatus(PyEnum):
    """Collection status enumeration"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    PROCESSING = "processing"
    ERROR = "error"


class Collection(Base, UUIDMixin, TimestampMixin):
    """Collection model for organizing documents"""

    __tablename__ = "collections"
    __table_args__ = {"schema": "collections"}

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id"), nullable=False)
    status = Column(Enum(CollectionStatus), default=CollectionStatus.ACTIVE, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)

    # Vector database configuration
    vector_collection_name = Column(String(255), nullable=False, unique=True)
    embedding_model = Column(String(100), nullable=False, default="text-embedding-004")
    embedding_dimensions = Column(Integer, nullable=False, default=768)

    # Processing configuration
    chunking_strategy = Column(String(50), nullable=False, default="recursive")
    chunk_size = Column(Integer, nullable=False, default=1000)
    chunk_overlap = Column(Integer, nullable=False, default=200)

    # Metadata
    document_count = Column(Integer, default=0, nullable=False)
    total_chunks = Column(Integer, default=0, nullable=False)
    settings = Column(JSON, nullable=True)

    # Relationships
    owner = relationship("User", back_populates="collections")
    files = relationship("File", back_populates="collection")
    chat_sessions = relationship("ChatSession", back_populates="collection")


# File Service Models
class FileStatus(PyEnum):
    """File processing status enumeration"""

    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    DELETED = "deleted"


class FileType(PyEnum):
    """Supported file types"""

    PDF = "pdf"
    TXT = "txt"
    CSV = "csv"
    DOCX = "docx"
    MD = "md"
    AUDIO = "audio"


class File(Base, UUIDMixin, TimestampMixin):
    """File model for document management"""

    __tablename__ = "files"
    __table_args__ = {"schema": "files"}

    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(Enum(FileType), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=False)

    # Processing status
    status = Column(Enum(FileStatus), default=FileStatus.UPLOADED, nullable=False)
    processing_started_at = Column(DateTime(timezone=True), nullable=True)
    processing_completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)

    # Collection association
    collection_id = Column(
        UUID(as_uuid=True), ForeignKey("collections.collections.id"), nullable=False
    )

    # Processing results
    total_chunks = Column(Integer, default=0, nullable=False)
    extracted_text_length = Column(Integer, default=0, nullable=False)
    file_metadata = Column(JSON, nullable=True)

    # Relationships
    collection = relationship("Collection", back_populates="files")
    chunks = relationship("DocumentChunk", back_populates="file")


class DocumentChunk(Base, UUIDMixin, TimestampMixin):
    """Document chunk model for processed text segments"""

    __tablename__ = "document_chunks"
    __table_args__ = {"schema": "files"}

    file_id = Column(UUID(as_uuid=True), ForeignKey("files.files.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    content_length = Column(Integer, nullable=False)

    # Vector database reference
    vector_id = Column(String(255), nullable=True)  # ID in vector database
    embedding_model = Column(String(100), nullable=False)

    # Chunk metadata
    page_number = Column(Integer, nullable=True)
    section_title = Column(String(255), nullable=True)
    chunk_metadata = Column(JSON, nullable=True)

    # Relationships
    file = relationship("File", back_populates="chunks")


# Chat Service Models
class ChatSessionStatus(PyEnum):
    """Chat session status enumeration"""

    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ChatSession(Base, UUIDMixin, TimestampMixin):
    """Chat session model"""

    __tablename__ = "chat_sessions"
    __table_args__ = {"schema": "chat"}

    user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id"), nullable=False)
    collection_id = Column(
        UUID(as_uuid=True), ForeignKey("collections.collections.id"), nullable=True
    )
    title = Column(String(255), nullable=False)
    status = Column(Enum(ChatSessionStatus), default=ChatSessionStatus.ACTIVE, nullable=False)

    # Chat configuration
    model_name = Column(String(100), nullable=False, default="gemini-2.0-flash-exp")
    temperature = Column(Float, nullable=False, default=0.1)
    max_tokens = Column(Integer, nullable=False, default=4000)

    # Session metadata
    message_count = Column(Integer, default=0, nullable=False)
    last_message_at = Column(DateTime(timezone=True), nullable=True)
    settings = Column(JSON, nullable=True)

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    collection = relationship("Collection", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session")


class MessageRole(PyEnum):
    """Chat message role enumeration"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(Base, UUIDMixin, TimestampMixin):
    """Chat message model"""

    __tablename__ = "chat_messages"
    __table_args__ = {"schema": "chat"}

    session_id = Column(UUID(as_uuid=True), ForeignKey("chat.chat_sessions.id"), nullable=False)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)

    # Message metadata
    token_count = Column(Integer, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    model_used = Column(String(100), nullable=True)

    # Context and sources
    context_chunks = Column(JSON, nullable=True)  # References to chunks used
    sources = Column(JSON, nullable=True)  # Source attribution
    message_metadata = Column(JSON, nullable=True)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")


# MCP Service Models
class MCPToolStatus(PyEnum):
    """MCP tool status enumeration"""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    ERROR = "error"
    DISABLED = "disabled"


class MCPTool(Base, UUIDMixin, TimestampMixin):
    """MCP tool registration model"""

    __tablename__ = "mcp_tools"
    __table_args__ = {"schema": "mcp"}

    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    version = Column(String(50), nullable=False)
    status = Column(Enum(MCPToolStatus), default=MCPToolStatus.AVAILABLE, nullable=False)

    # Tool configuration
    endpoint_url = Column(String(500), nullable=False)
    authentication_type = Column(String(50), nullable=True)
    configuration = Column(JSON, nullable=True)

    # Usage tracking
    usage_count = Column(Integer, default=0, nullable=False)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    error_count = Column(Integer, default=0, nullable=False)
    last_error_at = Column(DateTime(timezone=True), nullable=True)
    last_error_message = Column(Text, nullable=True)

    # Relationships
    executions = relationship("MCPExecution", back_populates="tool")


class MCPExecutionStatus(PyEnum):
    """MCP execution status enumeration"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class MCPExecution(Base, UUIDMixin, TimestampMixin):
    """MCP tool execution tracking"""

    __tablename__ = "mcp_executions"
    __table_args__ = {"schema": "mcp"}

    tool_id = Column(UUID(as_uuid=True), ForeignKey("mcp.mcp_tools.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat.chat_sessions.id"), nullable=True)

    # Execution details
    status = Column(Enum(MCPExecutionStatus), default=MCPExecutionStatus.PENDING, nullable=False)
    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)

    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    execution_time_ms = Column(Integer, nullable=True)

    # Relationships
    tool = relationship("MCPTool", back_populates="executions")
    user = relationship("User")
    session = relationship("ChatSession")
