"""
Collection Service Database Models
"""

import enum
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class CollectionStatus(enum.Enum):
    """Collection status enumeration"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    PROCESSING = "processing"


class AccessLevel(enum.Enum):
    """Access level enumeration"""

    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class Collection(Base):
    """Knowledge collection database model"""

    __tablename__ = "collections"
    __table_args__ = {"schema": "collections"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    owner_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    status = Column(Enum(CollectionStatus), default=CollectionStatus.ACTIVE, nullable=False)

    # Configuration and settings
    is_public = Column(Boolean, default=False, nullable=False)
    vector_collection_name = Column(String(255), nullable=False, unique=True)
    embedding_model = Column(String(100), nullable=False, default="text-embedding-3-small")
    embedding_dimensions = Column(Integer, nullable=False, default=1536)
    chunking_strategy = Column(String(50), nullable=False, default="fixed_size")
    chunk_size = Column(Integer, nullable=False, default=1000)
    chunk_overlap = Column(Integer, nullable=False, default=200)

    # Statistics
    document_count = Column(Integer, nullable=False, default=0)
    total_chunks = Column(Integer, nullable=False, default=0)

    # Metadata
    settings = Column(JSON, nullable=True, default=dict)  # Collection-specific settings

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    versions = relationship(
        "CollectionVersion", back_populates="collection", cascade="all, delete-orphan"
    )
    access_controls = relationship(
        "CollectionAccess", back_populates="collection", cascade="all, delete-orphan"
    )


class CollectionVersion(Base):
    """Collection version for tracking changes"""

    __tablename__ = "collection_versions"
    __table_args__ = {"schema": "collections"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    collection_id = Column(
        PGUUID(as_uuid=True), ForeignKey("collections.collections.id"), nullable=False
    )
    version_number = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)

    # Changes tracking
    changes = Column(JSON, nullable=False, default=dict)  # What changed in this version
    configuration_snapshot = Column(JSON, nullable=False, default=dict)  # Config at this version

    # Statistics at this version
    document_count = Column(Integer, nullable=False, default=0)
    total_chunks = Column(Integer, nullable=False, default=0)
    total_size_bytes = Column(Integer, nullable=False, default=0)

    # Metadata
    created_by = Column(PGUUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    collection = relationship("Collection", back_populates="versions")


class CollectionAccess(Base):
    """Collection access control"""

    __tablename__ = "collection_access"
    __table_args__ = {"schema": "collections"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    collection_id = Column(
        PGUUID(as_uuid=True), ForeignKey("collections.collections.id"), nullable=False
    )
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    access_level = Column(Enum(AccessLevel), nullable=False)

    # Permissions
    can_read = Column(Boolean, default=True, nullable=False)
    can_write = Column(Boolean, default=False, nullable=False)
    can_delete = Column(Boolean, default=False, nullable=False)
    can_manage_access = Column(Boolean, default=False, nullable=False)

    # Metadata
    granted_by = Column(PGUUID(as_uuid=True), nullable=False)
    granted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    collection = relationship("Collection", back_populates="access_controls")
