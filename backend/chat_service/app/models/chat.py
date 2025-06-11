"""
Chat Service Database Models
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class MessageRole(PyEnum):
    """Chat message role enumeration"""

    user = "user"
    assistant = "assistant"
    system = "system"


class ChatSession(Base):
    """Chat session database model"""

    __tablename__ = "chat_sessions"
    __table_args__ = {"schema": "chat"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    collection_ids = Column(JSON, nullable=False, default=list)  # List of collection UUIDs
    context_settings = Column(JSON, nullable=False, default=dict)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """Chat message database model"""

    __tablename__ = "chat_messages"
    __table_args__ = {"schema": "chat"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(PGUUID(as_uuid=True), ForeignKey("chat.chat_sessions.id"), nullable=False)
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    role = Column(Enum(MessageRole, schema="chat"), nullable=False)  # Use enum with schema
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON, nullable=False, default=dict)
    sources = Column(JSON, nullable=False, default=list)  # Source attribution data
    tokens_used = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")


class ChatContext(Base):
    """Chat context storage for RAG operations"""

    __tablename__ = "chat_contexts"
    __table_args__ = {"schema": "chat"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    message_id = Column(PGUUID(as_uuid=True), ForeignKey("chat.chat_messages.id"), nullable=False)
    query_embedding = Column(JSON, nullable=True)  # Stored as JSON array
    retrieved_chunks = Column(JSON, nullable=False, default=list)
    merged_context = Column(Text, nullable=True)
    context_meta = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# Pydantic models for API responses
class ChatSessionResponse(BaseModel):
    """Chat session API response model"""

    id: UUID
    user_id: UUID
    title: Optional[str]
    collection_ids: List[UUID]
    context_settings: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = None

    class Config:
        from_attributes = True


class ChatMessageResponse(BaseModel):
    """Chat message API response model"""

    id: UUID
    session_id: UUID
    user_id: UUID
    role: str
    content: str
    message_metadata: Dict[str, Any]
    sources: List[Dict[str, Any]]
    tokens_used: Optional[int]
    response_time_ms: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionCreate(BaseModel):
    """Chat session creation model"""

    title: Optional[str] = None
    collection_ids: List[UUID] = Field(default_factory=list)
    context_settings: Dict[str, Any] = Field(default_factory=dict)


class ChatMessageCreate(BaseModel):
    """Chat message creation model"""

    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1, max_length=50000)
    message_metadata: Dict[str, Any] = Field(default_factory=dict)
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    tokens_used: Optional[int] = None
    response_time_ms: Optional[int] = None
