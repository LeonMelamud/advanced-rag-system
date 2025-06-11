"""
Shared Database Models and Mixins
Common patterns and base classes for all services
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Boolean, Column, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.declarative import declarative_base

# Shared base for all models
Base = declarative_base()


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class UUIDMixin:
    """Mixin for UUID primary key"""

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)


class MetadataMixin:
    """Mixin for metadata fields (avoiding SQLAlchemy reserved 'metadata' name)"""

    meta_data = Column(JSON, nullable=False, default=dict)
    tags = Column(JSON, nullable=False, default=list)


class StatusMixin:
    """Mixin for common status fields"""

    is_active = Column(Boolean, default=True, nullable=False)


class StatsMixin:
    """Mixin for common statistics fields"""

    total_count = Column(Integer, nullable=False, default=0)
    success_count = Column(Integer, nullable=False, default=0)
    failure_count = Column(Integer, nullable=False, default=0)


class BaseModel(Base, UUIDMixin, TimestampMixin):
    """Base model with UUID and timestamps"""

    __abstract__ = True


class BaseModelWithMeta(BaseModel, MetadataMixin, StatusMixin):
    """Base model with UUID, timestamps, metadata, and status"""

    __abstract__ = True


class BaseModelWithStats(BaseModelWithMeta, StatsMixin):
    """Base model with UUID, timestamps, metadata, status, and stats"""

    __abstract__ = True
