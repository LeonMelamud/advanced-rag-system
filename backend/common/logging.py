"""Centralized logging configuration for Advanced RAG System"""

import json
import logging
import logging.config
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Log levels
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "structured")  # structured or simple
LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if hasattr(record, "service"):
            log_entry["service"] = record.service
        if hasattr(record, "operation"):
            log_entry["operation"] = record.operation
        if hasattr(record, "duration"):
            log_entry["duration_ms"] = record.duration

        return json.dumps(log_entry)


class SimpleFormatter(logging.Formatter):
    """Simple formatter for human-readable logs"""

    def __init__(self):
        super().__init__(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )


def setup_logging(
    service_name: str = "advanced_rag_system",
    log_level: str = LOG_LEVEL,
    log_format: str = LOG_FORMAT,
    log_file: Optional[str] = LOG_FILE,
) -> None:
    """Setup centralized logging configuration"""

    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    # Choose formatter
    if log_format.lower() == "structured":
        formatter = StructuredFormatter()
    else:
        formatter = SimpleFormatter()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, log_level))

    # File handler (if log file specified)
    handlers = [console_handler]
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, log_level))
        handlers.append(file_handler)

    # Configure root logger
    logging.basicConfig(level=getattr(logging, log_level), handlers=handlers, force=True)

    # Set service name for all loggers
    logging.getLogger().service = service_name

    # Configure specific loggers
    configure_library_loggers()


def configure_library_loggers():
    """Configure logging for third-party libraries"""

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("redis").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)

    # Keep our application logs at configured level
    logging.getLogger("backend").setLevel(getattr(logging, LOG_LEVEL))
    logging.getLogger("advanced_rag_system").setLevel(getattr(logging, LOG_LEVEL))


def get_logger(name: str) -> logging.Logger:
    """Get logger with service context"""
    logger = logging.getLogger(name)
    return logger


class LoggerAdapter(logging.LoggerAdapter):
    """Logger adapter for adding context to log messages"""

    def __init__(self, logger: logging.Logger, extra: Dict[str, Any]):
        super().__init__(logger, extra)

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """Process log message with extra context"""
        # Add extra fields to the log record
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        kwargs["extra"].update(self.extra)
        return msg, kwargs


def get_context_logger(
    name: str,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None,
    service: Optional[str] = None,
    operation: Optional[str] = None,
) -> LoggerAdapter:
    """Get logger with context information"""
    logger = get_logger(name)

    extra = {}
    if user_id:
        extra["user_id"] = user_id
    if request_id:
        extra["request_id"] = request_id
    if service:
        extra["service"] = service
    if operation:
        extra["operation"] = operation

    return LoggerAdapter(logger, extra)


# Performance logging utilities
class PerformanceLogger:
    """Utility for logging performance metrics"""

    def __init__(self, logger: logging.Logger, operation: str):
        self.logger = logger
        self.operation = operation
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.utcnow()
        self.logger.info(f"Starting operation: {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = (datetime.utcnow() - self.start_time).total_seconds() * 1000

            if exc_type:
                self.logger.error(
                    f"Operation failed: {self.operation}",
                    extra={"operation": self.operation, "duration": duration},
                )
            else:
                self.logger.info(
                    f"Operation completed: {self.operation}",
                    extra={"operation": self.operation, "duration": duration},
                )


def log_performance(operation: str):
    """Decorator for logging function performance"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            with PerformanceLogger(logger, operation):
                return func(*args, **kwargs)

        return wrapper

    return decorator


async def log_async_performance(operation: str):
    """Decorator for logging async function performance"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            with PerformanceLogger(logger, operation):
                return await func(*args, **kwargs)

        return wrapper

    return decorator


# Security logging utilities
class SecurityLogger:
    """Utility for logging security events"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def log_authentication_attempt(
        self,
        username: str,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        """Log authentication attempt"""
        event_type = "authentication_success" if success else "authentication_failure"

        self.logger.info(
            f"Authentication attempt: {username}",
            extra={
                "event_type": event_type,
                "username": username,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "success": success,
            },
        )

    def log_authorization_failure(
        self, user_id: str, resource: str, action: str, ip_address: Optional[str] = None
    ):
        """Log authorization failure"""
        self.logger.warning(
            f"Authorization denied: {user_id} attempted {action} on {resource}",
            extra={
                "event_type": "authorization_failure",
                "user_id": user_id,
                "resource": resource,
                "action": action,
                "ip_address": ip_address,
            },
        )

    def log_suspicious_activity(
        self,
        description: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Log suspicious activity"""
        self.logger.warning(
            f"Suspicious activity: {description}",
            extra={
                "event_type": "suspicious_activity",
                "user_id": user_id,
                "ip_address": ip_address,
                "details": details or {},
            },
        )


# Application-specific loggers
def get_auth_logger() -> SecurityLogger:
    """Get security logger for authentication events"""
    logger = get_logger("backend.auth")
    return SecurityLogger(logger)


def get_api_logger() -> logging.Logger:
    """Get logger for API requests"""
    return get_logger("backend.api")


def get_database_logger() -> logging.Logger:
    """Get logger for database operations"""
    return get_logger("backend.database")


def get_processing_logger() -> logging.Logger:
    """Get logger for document processing"""
    return get_logger("backend.processing")


def get_chat_logger() -> logging.Logger:
    """Get logger for chat operations"""
    return get_logger("backend.chat")


# Initialize logging on module import
if not logging.getLogger().handlers:
    setup_logging()
