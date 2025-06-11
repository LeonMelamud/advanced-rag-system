"""
Common utility functions for the Advanced RAG System.

This module contains utility functions that are shared across
all microservices in the system.
"""

import hashlib
import logging
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import magic
import structlog
from pydantic import BaseModel


def setup_logging(service_name: str, log_level: str = "INFO") -> structlog.stdlib.BoundLogger:
    """
    Set up structured logging for a service.

    Args:
        service_name: Name of the service
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Configured logger instance
    """
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level.upper()),
    )

    logger = structlog.get_logger(service_name)
    return logger


def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())


def generate_checksum(content: Union[str, bytes]) -> str:
    """
    Generate SHA256 checksum for content.

    Args:
        content: Content to hash (string or bytes)

    Returns:
        SHA256 hash as hex string
    """
    if isinstance(content, str):
        content = content.encode("utf-8")

    return hashlib.sha256(content).hexdigest()


def detect_mime_type(file_path: Union[str, Path]) -> str:
    """
    Detect MIME type of a file using python-magic.

    Args:
        file_path: Path to the file

    Returns:
        MIME type string
    """
    try:
        mime = magic.Magic(mime=True)
        return mime.from_file(str(file_path))
    except Exception:
        # Fallback to basic detection based on extension
        file_path = Path(file_path)
        extension = file_path.suffix.lower()

        mime_map = {
            ".pdf": "application/pdf",
            ".csv": "text/csv",
            ".txt": "text/plain",
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".m4a": "audio/mp4",
            ".json": "application/json",
            ".xml": "application/xml",
            ".html": "text/html",
            ".md": "text/markdown",
        }

        return mime_map.get(extension, "application/octet-stream")


def get_file_size(file_path: Union[str, Path]) -> int:
    """
    Get file size in bytes.

    Args:
        file_path: Path to the file

    Returns:
        File size in bytes
    """
    return os.path.getsize(file_path)


def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def validate_file_size(file_size: int, max_size_mb: int = 100) -> bool:
    """
    Validate file size against maximum allowed size.

    Args:
        file_size: File size in bytes
        max_size_mb: Maximum allowed size in MB

    Returns:
        True if file size is valid, False otherwise
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_size_bytes


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing/replacing unsafe characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove or replace unsafe characters
    unsafe_chars = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]
    sanitized = filename

    for char in unsafe_chars:
        sanitized = sanitized.replace(char, "_")

    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip(" .")

    # Ensure filename is not empty
    if not sanitized:
        sanitized = f"file_{generate_uuid()[:8]}"

    return sanitized


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.

    Args:
        items: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two dictionaries, with dict2 values taking precedence.

    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)

    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    result.update(dict2)
    return result


def extract_file_extension(filename: str) -> str:
    """
    Extract file extension from filename.

    Args:
        filename: Filename to extract extension from

    Returns:
        File extension (without dot) in lowercase
    """
    return Path(filename).suffix.lower().lstrip(".")


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)

    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1

    return f"{size:.1f} {size_names[i]}"


def validate_uuid(uuid_string: str) -> bool:
    """
    Validate if a string is a valid UUID.

    Args:
        uuid_string: String to validate

    Returns:
        True if valid UUID, False otherwise
    """
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False


def safe_json_loads(json_string: str, default: Any = None) -> Any:
    """
    Safely load JSON string with fallback.

    Args:
        json_string: JSON string to parse
        default: Default value if parsing fails

    Returns:
        Parsed JSON or default value
    """
    try:
        import json

        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length with suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def get_env_var(name: str, default: Optional[str] = None, required: bool = False) -> str:
    """
    Get environment variable with optional default and validation.

    Args:
        name: Environment variable name
        default: Default value if not found
        required: Whether the variable is required

    Returns:
        Environment variable value

    Raises:
        ValueError: If required variable is not found
    """
    value = os.getenv(name, default)

    if required and value is None:
        raise ValueError(f"Required environment variable '{name}' not found")

    return value


def create_error_response(
    error: str, details: Optional[List[Dict[str, Any]]] = None, request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create standardized error response.

    Args:
        error: Error message
        details: Optional error details
        request_id: Optional request ID

    Returns:
        Error response dictionary
    """
    return {
        "error": error,
        "details": details or [],
        "timestamp": utc_now().isoformat(),
        "request_id": request_id,
    }


class Timer:
    """Context manager for timing operations."""

    def __init__(self, logger: Optional[Any] = None, operation: str = "operation"):
        self.logger = logger
        self.operation = operation
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        if self.logger:
            self.logger.info(f"Starting {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()

        if self.logger:
            if exc_type is None:
                self.logger.info(f"Completed {self.operation}", duration=duration)
            else:
                self.logger.error(f"Failed {self.operation}", duration=duration, error=str(exc_val))

    @property
    def duration(self) -> Optional[float]:
        """Get operation duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


def get_service_info() -> Dict[str, Any]:
    """
    Get basic service information.

    Returns:
        Dictionary with service information
    """
    return {
        "timestamp": utc_now().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
    }
