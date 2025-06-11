"""
MCP Orchestrator Database Models
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


class ToolStatus(enum.Enum):
    """Tool status enumeration"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    ERROR = "error"


class ToolType(enum.Enum):
    """Tool type enumeration"""

    FUNCTION = "function"
    API = "api"
    SCRIPT = "script"
    WEBHOOK = "webhook"


class ExecutionStatus(enum.Enum):
    """Execution status enumeration"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class Tool(Base):
    """MCP Tool database model"""

    __tablename__ = "tools"
    __table_args__ = {"schema": "mcp"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    owner_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    tool_type = Column(Enum(ToolType), nullable=False)
    status = Column(Enum(ToolStatus), default=ToolStatus.ACTIVE, nullable=False)

    # Tool Configuration
    configuration = Column(JSON, nullable=False, default=dict)
    parameters_schema = Column(JSON, nullable=False, default=dict)  # JSON Schema for parameters
    return_schema = Column(JSON, nullable=False, default=dict)  # JSON Schema for return values

    # Tool Implementation
    implementation = Column(JSON, nullable=False, default=dict)  # Code, URL, or execution details

    # Metadata
    tags = Column(JSON, nullable=False, default=list)  # List of tags
    tool_metadata = Column(JSON, nullable=False, default=dict)
    version = Column(String(50), nullable=False, default="1.0.0")

    # Usage Statistics
    execution_count = Column(Integer, nullable=False, default=0)
    success_count = Column(Integer, nullable=False, default=0)
    failure_count = Column(Integer, nullable=False, default=0)
    avg_execution_time_ms = Column(Integer, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_executed_at = Column(DateTime, nullable=True)

    # Relationships
    executions = relationship("ToolExecution", back_populates="tool", cascade="all, delete-orphan")


class ToolExecution(Base):
    """Tool execution history"""

    __tablename__ = "tool_executions"
    __table_args__ = {"schema": "mcp"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tool_id = Column(PGUUID(as_uuid=True), ForeignKey("mcp.tools.id"), nullable=False)
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    session_id = Column(PGUUID(as_uuid=True), nullable=True)  # Optional chat session reference

    # Execution Details
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING, nullable=False)
    input_parameters = Column(JSON, nullable=False, default=dict)
    output_result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)

    # Performance Metrics
    execution_time_ms = Column(Integer, nullable=True)
    memory_used_mb = Column(Integer, nullable=True)
    cpu_usage_percent = Column(Integer, nullable=True)

    # Metadata
    execution_context = Column(JSON, nullable=False, default=dict)
    execution_metadata = Column(JSON, nullable=False, default=dict)

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    tool = relationship("Tool", back_populates="executions")


class ToolAccess(Base):
    """Tool access control"""

    __tablename__ = "tool_access"
    __table_args__ = {"schema": "mcp"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tool_id = Column(PGUUID(as_uuid=True), ForeignKey("mcp.tools.id"), nullable=False)
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Permissions
    can_execute = Column(Boolean, default=True, nullable=False)
    can_view = Column(Boolean, default=True, nullable=False)
    can_modify = Column(Boolean, default=False, nullable=False)

    # Metadata
    granted_by = Column(PGUUID(as_uuid=True), nullable=False)
    granted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    tool = relationship("Tool")


class ToolRegistry(Base):
    """Tool registry for system-wide tool management"""

    __tablename__ = "tool_registry"
    __table_args__ = {"schema": "mcp"}

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, unique=True, index=True)
    category = Column(String(100), nullable=False, index=True)

    # Registry Information
    registry_url = Column(String(500), nullable=True)
    documentation_url = Column(String(500), nullable=True)
    source_url = Column(String(500), nullable=True)

    # Tool Information
    latest_version = Column(String(50), nullable=False)
    supported_versions = Column(JSON, nullable=False, default=list)
    compatibility = Column(JSON, nullable=False, default=dict)

    # Metadata
    description = Column(Text, nullable=True)
    author = Column(String(255), nullable=True)
    license = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=False, default=list)

    # Status
    is_verified = Column(Boolean, default=False, nullable=False)
    is_deprecated = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    parameters = Column(JSON, nullable=False, default=dict)
    tool_metadata = Column(JSON, nullable=False, default=dict)
    is_active = Column(Boolean, default=True, nullable=False)
