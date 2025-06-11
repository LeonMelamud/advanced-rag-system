"""Global exception handling for Advanced RAG System"""

import logging
import traceback
from datetime import datetime
from typing import Any, Dict, Optional, Union

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


# Custom Exception Classes
class BaseAPIException(Exception):
    """Base exception for API errors"""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(BaseAPIException):
    """Validation error"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class AuthenticationError(BaseAPIException):
    """Authentication error"""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR",
        )


class AuthorizationError(BaseAPIException):
    """Authorization error"""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message, status_code=status.HTTP_403_FORBIDDEN, error_code="AUTHORIZATION_ERROR"
        )


class NotFoundError(BaseAPIException):
    """Resource not found error"""

    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        super().__init__(
            message=message, status_code=status.HTTP_404_NOT_FOUND, error_code="NOT_FOUND"
        )


class ConflictError(BaseAPIException):
    """Resource conflict error"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT_ERROR",
            details=details,
        )


class RateLimitError(BaseAPIException):
    """Rate limit exceeded error"""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_ERROR",
        )


class ExternalServiceError(BaseAPIException):
    """External service error"""

    def __init__(self, service: str, message: str = None):
        message = message or f"External service '{service}' is unavailable"
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service},
        )


class DatabaseError(BaseAPIException):
    """Database operation error"""

    def __init__(self, message: str = "Database operation failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
        )


class ProcessingError(BaseAPIException):
    """Document processing error"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="PROCESSING_ERROR",
            details=details,
        )


# Error Response Models
class ErrorDetail(BaseModel):
    """Error detail model"""

    field: Optional[str] = None
    message: str
    code: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standardized error response model"""

    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    request_id: Optional[str] = None
    path: Optional[str] = None


# Utility Functions
def get_request_id(request: Request) -> Optional[str]:
    """Extract request ID from headers"""
    return request.headers.get("X-Request-ID") or request.headers.get("x-request-id")


def create_error_response(
    error_code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None,
) -> ErrorResponse:
    """Create standardized error response"""
    return ErrorResponse(
        error_code=error_code,
        message=message,
        details=details,
        timestamp=datetime.utcnow(),
        request_id=get_request_id(request) if request else None,
        path=str(request.url.path) if request else None,
    )


# Exception Handlers
async def base_api_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """Handle custom API exceptions"""
    logger.error(
        f"API Exception: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "details": exc.details,
            "request_id": get_request_id(request),
            "path": str(request.url.path),
        },
    )

    error_response = create_error_response(
        error_code=exc.error_code, message=exc.message, details=exc.details, request=request
    )

    return JSONResponse(status_code=exc.status_code, content=error_response.dict())


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions"""
    error_code = "HTTP_ERROR"

    # Map common HTTP status codes to error codes
    status_code_mapping = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        422: "VALIDATION_ERROR",
        500: "INTERNAL_ERROR",
    }

    error_code = status_code_mapping.get(exc.status_code, error_code)

    logger.error(
        f"HTTP Exception: {exc.status_code} - {exc.detail}",
        extra={
            "error_code": error_code,
            "status_code": exc.status_code,
            "request_id": get_request_id(request),
            "path": str(request.url.path),
        },
    )

    error_response = create_error_response(
        error_code=error_code, message=str(exc.detail), request=request
    )

    return JSONResponse(status_code=exc.status_code, content=error_response.dict())


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append({"field": field, "message": error["msg"], "code": error["type"]})

    logger.warning(
        f"Validation Error: {len(errors)} validation errors",
        extra={
            "error_code": "VALIDATION_ERROR",
            "validation_errors": errors,
            "request_id": get_request_id(request),
            "path": str(request.url.path),
        },
    )

    error_response = create_error_response(
        error_code="VALIDATION_ERROR",
        message="Request validation failed",
        details={"errors": errors},
        request=request,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=error_response.dict()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    logger.error(
        f"Unexpected Exception: {type(exc).__name__} - {str(exc)}",
        extra={
            "error_code": "INTERNAL_ERROR",
            "exception_type": type(exc).__name__,
            "traceback": traceback.format_exc(),
            "request_id": get_request_id(request),
            "path": str(request.url.path),
        },
    )

    # Don't expose internal error details in production
    message = "An internal error occurred"
    details = None

    # In development, include more details
    import os

    if os.getenv("ENVIRONMENT", "production").lower() in ["development", "dev", "local"]:
        message = f"{type(exc).__name__}: {str(exc)}"
        details = {"traceback": traceback.format_exc()}

    error_response = create_error_response(
        error_code="INTERNAL_ERROR", message=message, details=details, request=request
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error_response.dict()
    )


# Exception Handler Registration
def register_exception_handlers(app):
    """Register all exception handlers with FastAPI app"""

    # Custom API exceptions
    app.add_exception_handler(BaseAPIException, base_api_exception_handler)

    # FastAPI HTTP exceptions
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)

    # Validation errors
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # General exceptions (catch-all)
    app.add_exception_handler(Exception, general_exception_handler)


# Context Managers for Error Handling
class ErrorContext:
    """Context manager for handling errors in specific operations"""

    def __init__(self, operation: str, logger: logging.Logger = None):
        self.operation = operation
        self.logger = logger or logging.getLogger(__name__)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.logger.error(
                f"Error in {self.operation}: {exc_val}",
                extra={
                    "operation": self.operation,
                    "exception_type": exc_type.__name__,
                    "traceback": traceback.format_exc(),
                },
            )
        return False  # Don't suppress the exception


# Utility decorators
def handle_database_errors(func):
    """Decorator to handle database errors"""

    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Database error in {func.__name__}: {e}")
            raise DatabaseError(f"Database operation failed: {str(e)}")

    return wrapper


def handle_external_service_errors(service_name: str):
    """Decorator to handle external service errors"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"External service error in {service_name}: {e}")
                raise ExternalServiceError(service_name, str(e))

        return wrapper

    return decorator
