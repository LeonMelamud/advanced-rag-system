"""
File Models for File Service
Uses shared models and adds file service specific models
"""

import enum
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Enum, ForeignKey, Integer, String, Text

# Import shared models
from backend.common.database.models import DocumentChunk, File, FileStatus, FileType

# Import shared base classes
from backend.common.models import BaseModel


class ChunkingStrategy(str, enum.Enum):
    """Available chunking strategies"""

    FIXED = "fixed"
    RECURSIVE = "recursive"
    SEMANTIC = "semantic"
    PARAGRAPH = "paragraph"


class ProcessingJob(BaseModel):
    """Processing job model for tracking async file processing"""

    __tablename__ = "processing_jobs"
    __table_args__ = {"schema": "files"}

    # Job information
    file_id = Column(String(36), ForeignKey("files.files.id"), nullable=False, index=True)
    job_type = Column(String(50), nullable=False)  # 'text_extraction', 'chunking', 'embedding'
    status = Column(Enum(FileStatus), default=FileStatus.PROCESSING, nullable=False)

    # Processing details
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)

    # Job configuration
    job_config = Column(JSON, nullable=True)  # Store job-specific configuration

    # Progress tracking
    progress_percentage = Column(Integer, default=0)
    current_step = Column(String(100), nullable=True)

    def __repr__(self):
        return f"<ProcessingJob(id={self.id}, file_id={self.file_id}, job_type={self.job_type}, status={self.status})>"

    @property
    def is_completed(self) -> bool:
        """Check if job is completed"""
        return self.status == FileStatus.PROCESSED

    @property
    def is_failed(self) -> bool:
        """Check if job failed"""
        return self.status == FileStatus.FAILED


# Alias the shared models for backward compatibility
FileChunk = DocumentChunk
