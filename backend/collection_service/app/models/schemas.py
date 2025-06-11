"""
Collection Service Pydantic Schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from .collection import AccessLevel, CollectionStatus


# Collection Schemas
class CollectionCreate(BaseModel):
    """Collection creation schema"""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    is_public: bool = Field(default=False)
    embedding_model: str = Field(default="text-embedding-3-small", max_length=100)
    embedding_dimensions: int = Field(default=1536, ge=100, le=4096)
    chunking_strategy: str = Field(default="fixed_size", max_length=50)
    chunk_size: int = Field(default=1000, ge=100, le=10000)
    chunk_overlap: int = Field(default=200, ge=0, le=1000)
    settings: Dict[str, Any] = Field(default_factory=dict)


class CollectionUpdate(BaseModel):
    """Collection update schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[CollectionStatus] = None
    is_public: Optional[bool] = None
    embedding_model: Optional[str] = Field(None, max_length=100)
    embedding_dimensions: Optional[int] = Field(None, ge=100, le=4096)
    chunking_strategy: Optional[str] = Field(None, max_length=50)
    chunk_size: Optional[int] = Field(None, ge=100, le=10000)
    chunk_overlap: Optional[int] = Field(None, ge=0, le=1000)
    settings: Optional[Dict[str, Any]] = None


class CollectionResponse(BaseModel):
    """Collection response schema"""

    id: UUID
    name: str
    description: Optional[str]
    owner_id: UUID
    status: CollectionStatus
    is_public: bool
    vector_collection_name: str
    embedding_model: str
    embedding_dimensions: int
    chunking_strategy: str
    chunk_size: int
    chunk_overlap: int
    settings: Dict[str, Any] = Field(default_factory=dict)
    document_count: int
    total_chunks: int
    created_at: datetime
    updated_at: datetime

    @field_validator("settings", mode="before")
    @classmethod
    def validate_settings(cls, v):
        """Convert None to empty dict"""
        return v if v is not None else {}

    class Config:
        from_attributes = True


class CollectionListResponse(BaseModel):
    """Collection list response schema"""

    collections: List[CollectionResponse]
    total_count: int
    has_more: bool


# Collection Version Schemas
class CollectionVersionCreate(BaseModel):
    """Collection version creation schema"""

    description: Optional[str] = Field(None, max_length=1000)
    changes: Dict[str, Any] = Field(default_factory=dict)


class CollectionVersionResponse(BaseModel):
    """Collection version response schema"""

    id: UUID
    collection_id: UUID
    version_number: int
    description: Optional[str]
    changes: Dict[str, Any]
    configuration_snapshot: Dict[str, Any]
    document_count: int
    total_chunks: int
    total_size_bytes: int
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class CollectionVersionListResponse(BaseModel):
    """Collection version list response schema"""

    versions: List[CollectionVersionResponse]
    total: int
    limit: int
    offset: int


class VersionComparisonResponse(BaseModel):
    """Version comparison response schema"""

    collection_id: UUID
    version1: int
    version2: int
    differences: Dict[str, Any]
    summary: str
    created_at: datetime

    class Config:
        from_attributes = True


# Collection Access Schemas
class CollectionAccessCreate(BaseModel):
    """Collection access creation schema"""

    user_id: UUID
    access_level: AccessLevel
    can_read: bool = True
    can_write: bool = False
    can_delete: bool = False
    can_manage_access: bool = False
    expires_at: Optional[datetime] = None


class CollectionAccessUpdate(BaseModel):
    """Collection access update schema"""

    access_level: Optional[AccessLevel] = None
    can_read: Optional[bool] = None
    can_write: Optional[bool] = None
    can_delete: Optional[bool] = None
    can_manage_access: Optional[bool] = None
    expires_at: Optional[datetime] = None


class CollectionAccessResponse(BaseModel):
    """Collection access response schema"""

    id: UUID
    collection_id: UUID
    user_id: UUID
    access_level: AccessLevel
    can_read: bool
    can_write: bool
    can_delete: bool
    can_manage_access: bool
    granted_by: UUID
    granted_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True


# Collection Statistics
class CollectionStats(BaseModel):
    """Collection statistics schema"""

    collection_id: UUID
    document_count: int
    total_chunks: int
    embedding_model: str
    chunking_strategy: str
    chunk_size: int
    chunk_overlap: int
    created_at: datetime
    updated_at: datetime


# Collection Configuration
class CollectionConfig(BaseModel):
    """Collection configuration schema"""

    embedding_model: str
    embedding_dimensions: int
    chunking_strategy: str
    chunk_size: int
    chunk_overlap: int
    settings: Dict[str, Any] = Field(default_factory=dict)
