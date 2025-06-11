"""
Shared API Patterns and Response Models
Common API patterns for all services
"""

import logging
import time
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict, Generic, List, Optional, TypeVar
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Import shared utilities
from .utils import get_service_info

T = TypeVar("T")

logger = logging.getLogger(__name__)


class BaseResponse(BaseModel):
    """Base response model"""

    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DataResponse(BaseResponse, Generic[T]):
    """Response model with data"""

    data: T


class ListResponse(BaseResponse, Generic[T]):
    """Response model for list data with pagination"""

    data: List[T]
    total: int
    page: int = 1
    page_size: int = 10
    has_next: bool = False
    has_prev: bool = False


class ErrorResponse(BaseResponse):
    """Error response model"""

    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Shared health check response model"""

    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    service: str = Field(..., description="Service name")
    version: str = Field(default="1.0.0", description="Service version")
    dependencies: Dict[str, Any] = Field(
        default_factory=dict, description="Dependency health status"
    )


class BaseCreateModel(BaseModel):
    """Base model for creation requests"""

    pass


class BaseUpdateModel(BaseModel):
    """Base model for update requests"""

    pass


class BaseQueryParams(BaseModel):
    """Base query parameters for list endpoints"""

    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Items per page")
    search: Optional[str] = Field(None, description="Search term")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_order: str = Field("asc", pattern="^(asc|desc)$", description="Sort order")


class DependencyCheck:
    """Base class for dependency health checks"""

    def __init__(self, name: str, check_func: Callable[[], Awaitable[Dict[str, Any]]]):
        self.name = name
        self.check_func = check_func

    async def check(self) -> Dict[str, Any]:
        """Execute the dependency check"""
        try:
            start_time = time.time()
            result = await self.check_func()
            response_time = int((time.time() - start_time) * 1000)

            # Ensure result has required fields
            if "status" not in result:
                result["status"] = "healthy"
            if "response_time_ms" not in result:
                result["response_time_ms"] = response_time

            return result
        except Exception as e:
            return {"status": "unhealthy", "error": str(e), "details": f"{self.name} check failed"}


def create_health_router(
    service_name: str,
    version: str = "1.0.0",
    dependency_checks: Optional[List[DependencyCheck]] = None,
    critical_dependencies: Optional[List[str]] = None,
) -> APIRouter:
    """
    Create a standardized health check router for any service

    Args:
        service_name: Name of the service
        version: Service version
        dependency_checks: List of dependency checks to perform
        critical_dependencies: List of critical dependency names for readiness check
    """
    router = APIRouter()
    dependency_checks = dependency_checks or []
    critical_dependencies = critical_dependencies or []

    async def check_all_dependencies() -> Dict[str, Any]:
        """Check all configured dependencies"""
        dependencies = {}

        for dep_check in dependency_checks:
            dependencies[dep_check.name] = await dep_check.check()

        return dependencies

    @router.get("/", response_model=HealthResponse)
    async def health_check():
        """Basic health check endpoint"""
        try:
            # Check all dependencies
            dependencies = await check_all_dependencies()

            # Determine overall status
            overall_status = "healthy"
            for dep_name, dep_status in dependencies.items():
                if dep_status.get("status") != "healthy":
                    overall_status = "degraded"
                    break

            return HealthResponse(
                status=overall_status,
                timestamp=datetime.utcnow(),
                service=service_name,
                version=version,
                dependencies=dependencies,
            )

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service unhealthy"
            )

    @router.get("/ready")
    async def readiness_check():
        """Readiness check for Kubernetes"""
        try:
            # Check if service is ready to handle requests
            dependencies = await check_all_dependencies()

            # Service is ready if critical dependencies are healthy
            for dep in critical_dependencies:
                if dep in dependencies and dependencies[dep].get("status") != "healthy":
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail=f"Critical dependency {dep} is not healthy",
                    )

            return {"status": "ready", "timestamp": datetime.utcnow()}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Readiness check failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service not ready"
            )

    @router.get("/live")
    async def liveness_check():
        """Liveness check for Kubernetes"""
        try:
            # Basic liveness check - service is running
            return {"status": "alive", "timestamp": datetime.utcnow(), **get_service_info()}

        except Exception as e:
            logger.error(f"Liveness check failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service not alive"
            )

    return router


# Legacy health router for backward compatibility
router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Legacy health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        service="unknown",
        version="1.0.0",
        dependencies={},
    )


def create_error_handler():
    """Create standard error handler"""

    async def global_exception_handler(request, exc):
        """Global exception handler"""
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                message="Internal server error",
                error_code="INTERNAL_ERROR",
                details={"error": str(exc)},
            ).dict(),
        )

    return global_exception_handler


def create_crud_responses():
    """Create standard CRUD response patterns"""
    return {
        201: {"description": "Created successfully"},
        400: {"description": "Bad request", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse},
        403: {"description": "Forbidden", "model": ErrorResponse},
        404: {"description": "Not found", "model": ErrorResponse},
        409: {"description": "Conflict", "model": ErrorResponse},
        422: {"description": "Validation error", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse},
    }
