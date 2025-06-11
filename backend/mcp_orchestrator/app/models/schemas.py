"""
MCP Orchestrator Pydantic Schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .tool import ExecutionStatus, ToolStatus, ToolType


# Tool Schemas
class ToolCreate(BaseModel):
    """Tool creation schema"""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    tool_type: ToolType
    configuration: Dict[str, Any] = Field(default_factory=dict)
    parameters_schema: Dict[str, Any] = Field(default_factory=dict)
    return_schema: Dict[str, Any] = Field(default_factory=dict)
    implementation: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    tool_metadata: Dict[str, Any] = Field(default_factory=dict)
    version: str = Field(default="1.0.0", max_length=50)


class ToolUpdate(BaseModel):
    """Tool update schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[ToolStatus] = None
    configuration: Optional[Dict[str, Any]] = None
    parameters_schema: Optional[Dict[str, Any]] = None
    return_schema: Optional[Dict[str, Any]] = None
    implementation: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    tool_metadata: Optional[Dict[str, Any]] = None
    version: Optional[str] = Field(None, max_length=50)


class ToolResponse(BaseModel):
    """Tool response schema"""

    id: UUID
    name: str
    description: Optional[str]
    owner_id: UUID
    tool_type: ToolType
    status: ToolStatus
    configuration: Dict[str, Any]
    parameters_schema: Dict[str, Any]
    return_schema: Dict[str, Any]
    implementation: Dict[str, Any]
    tags: List[str]
    tool_metadata: Dict[str, Any]
    version: str
    execution_count: int
    success_count: int
    failure_count: int
    avg_execution_time_ms: Optional[int]
    created_at: datetime
    updated_at: datetime
    last_executed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ToolListResponse(BaseModel):
    """Tool list response schema"""

    tools: List[ToolResponse]
    total: int
    limit: int
    offset: int


# Tool Execution Schemas
class ToolExecutionRequest(BaseModel):
    """Tool execution request schema"""

    tool_id: UUID
    input_parameters: Dict[str, Any] = Field(default_factory=dict)
    session_id: Optional[UUID] = None
    execution_context: Dict[str, Any] = Field(default_factory=dict)
    execution_metadata: Dict[str, Any] = Field(default_factory=dict)


class ToolExecutionResponse(BaseModel):
    """Tool execution response schema"""

    id: UUID
    tool_id: UUID
    user_id: UUID
    session_id: Optional[UUID]
    status: ExecutionStatus
    input_parameters: Dict[str, Any]
    output_result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    execution_time_ms: Optional[int]
    memory_used_mb: Optional[int]
    cpu_usage_percent: Optional[int]
    execution_context: Dict[str, Any]
    execution_metadata: Dict[str, Any]
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ToolExecutionListResponse(BaseModel):
    """Tool execution list response schema"""

    executions: List[ToolExecutionResponse]
    total: int
    limit: int
    offset: int


# Tool Access Schemas
class ToolAccessCreate(BaseModel):
    """Tool access creation schema"""

    user_id: UUID
    can_execute: bool = True
    can_view: bool = True
    can_modify: bool = False
    expires_at: Optional[datetime] = None


class ToolAccessUpdate(BaseModel):
    """Tool access update schema"""

    can_execute: Optional[bool] = None
    can_view: Optional[bool] = None
    can_modify: Optional[bool] = None
    expires_at: Optional[datetime] = None


class ToolAccessResponse(BaseModel):
    """Tool access response schema"""

    id: UUID
    tool_id: UUID
    user_id: UUID
    can_execute: bool
    can_view: bool
    can_modify: bool
    granted_by: UUID
    granted_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True


# Tool Registry Schemas
class ToolRegistryCreate(BaseModel):
    """Tool registry creation schema"""

    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=100)
    registry_url: Optional[str] = Field(None, max_length=500)
    documentation_url: Optional[str] = Field(None, max_length=500)
    source_url: Optional[str] = Field(None, max_length=500)
    latest_version: str = Field(..., max_length=50)
    supported_versions: List[str] = Field(default_factory=list)
    compatibility: Dict[str, Any] = Field(default_factory=dict)
    description: Optional[str] = Field(None, max_length=2000)
    author: Optional[str] = Field(None, max_length=255)
    license: Optional[str] = Field(None, max_length=100)
    tags: List[str] = Field(default_factory=list)


class ToolRegistryResponse(BaseModel):
    """Tool registry response schema"""

    id: UUID
    name: str
    category: str
    registry_url: Optional[str]
    documentation_url: Optional[str]
    source_url: Optional[str]
    latest_version: str
    supported_versions: List[str]
    compatibility: Dict[str, Any]
    description: Optional[str]
    author: Optional[str]
    license: Optional[str]
    tags: List[str]
    is_verified: bool
    is_deprecated: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Tool Statistics
class ToolStats(BaseModel):
    """Tool statistics schema"""

    tool_id: UUID
    execution_count: int
    success_count: int
    failure_count: int
    success_rate: float
    avg_execution_time_ms: Optional[int]
    last_executed_at: Optional[datetime]
    total_users: int
    active_users_last_30_days: int


class ToolStatsResponse(BaseModel):
    """Tool statistics response schema"""

    tool_id: UUID
    execution_count: int
    success_count: int
    failure_count: int
    success_rate: float
    avg_execution_time_ms: Optional[int]
    last_executed_at: Optional[datetime]
    total_users: int
    active_users_last_30_days: int

    class Config:
        from_attributes = True


# Tool Validation
class ToolValidationResult(BaseModel):
    """Tool validation result schema"""

    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


# Execution Context
class ExecutionContext(BaseModel):
    """Execution context schema"""

    user_id: UUID
    session_id: Optional[UUID] = None
    environment: str = "sandbox"
    timeout_seconds: int = 30
    max_memory_mb: int = 512
    max_cpu_percent: float = 50.0
    allowed_domains: List[str] = Field(default_factory=list)
    blocked_domains: List[str] = Field(default_factory=list)
    custom_headers: Dict[str, str] = Field(default_factory=dict)
