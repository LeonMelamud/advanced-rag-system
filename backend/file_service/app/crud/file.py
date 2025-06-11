"""
File CRUD Operations
Database operations for file management following DRY principles
Updated to work with existing shared models
"""

import hashlib
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiofiles
import magic
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import and_, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.file_service.app.models.file import (
    ChunkingStrategy,
    File,
    FileChunk,
    FileStatus,
    FileType,
    ProcessingJob,
)


class FileCRUD:
    """File CRUD operations following DRY principles"""

    @staticmethod
    async def get_file_by_id(db: AsyncSession, file_id: str, user_id: str = None) -> Optional[File]:
        """Get file by ID, optionally filtered by user"""
        query = select(File).filter(File.id == file_id)

        if user_id:
            from backend.common.database.models import Collection

            query = query.join(Collection).filter(Collection.owner_id == user_id)

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_files_by_user(
        db: AsyncSession,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[FileStatus] = None,
        file_type: Optional[FileType] = None,
    ) -> List[File]:
        """Get files for a specific user with optional filtering"""
        from backend.common.database.models import Collection

        query = select(File).join(Collection).filter(Collection.owner_id == user_id)

        if status:
            query = query.filter(File.status == status)
        if file_type:
            query = query.filter(File.file_type == file_type)

        query = query.offset(skip).limit(limit).order_by(File.created_at.desc())

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_file_by_checksum(db: AsyncSession, checksum: str, user_id: str) -> Optional[File]:
        """Get file by checksum to detect duplicates within user's collections"""
        from backend.common.database.models import Collection

        # Check for files with matching checksum in metadata
        result = await db.execute(
            select(File)
            .join(Collection)
            .filter(
                and_(
                    Collection.owner_id == user_id,
                    File.file_metadata.op("->>")("checksum") == checksum,
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    def calculate_file_checksum(file_content: bytes) -> str:
        """Calculate SHA-256 checksum of file content"""
        return hashlib.sha256(file_content).hexdigest()

    @staticmethod
    def detect_file_type(filename: str, mime_type: str) -> FileType:
        """Detect file type from filename and MIME type"""
        extension = filename.split(".")[-1].lower() if "." in filename else ""

        # PDF files
        if extension == "pdf" or "pdf" in mime_type.lower():
            return FileType.PDF

        # CSV files
        if extension == "csv" or "csv" in mime_type.lower():
            return FileType.CSV

        # Text files
        if extension in ["txt", "text"] or "text/plain" in mime_type.lower():
            return FileType.TXT

        # DOCX files
        if extension == "docx" or "wordprocessingml" in mime_type.lower():
            return FileType.DOCX

        # Markdown files
        if extension == "md" or extension == "markdown":
            return FileType.MD

        # Audio files
        if extension in ["mp3", "wav", "flac", "m4a", "ogg"] or "audio" in mime_type.lower():
            return FileType.AUDIO

        return FileType.TXT  # Default fallback

    @staticmethod
    async def get_or_create_default_collection(db: AsyncSession, user_id: str) -> str:
        """Get or create a default collection for the user"""
        from backend.common.database.models import Collection, CollectionStatus

        # Try to find existing default collection
        result = await db.execute(
            select(Collection).filter(
                and_(Collection.owner_id == user_id, Collection.name == "Default Files")
            )
        )
        collection = result.scalar_one_or_none()

        if not collection:
            # Create default collection
            collection = Collection(
                name="Default Files",
                description="Default collection for uploaded files",
                owner_id=user_id,
                status=CollectionStatus.ACTIVE,
                vector_collection_name=f"user_{user_id}_default",
                embedding_model="text-embedding-3-small",
                embedding_dimensions=1536,
                chunking_strategy="recursive",
                chunk_size=1000,
                chunk_overlap=200,
            )
            db.add(collection)
            await db.commit()
            await db.refresh(collection)

        return collection.id

    @staticmethod
    async def create_file(
        db: AsyncSession,
        upload_file: UploadFile,
        user_id: str,
        storage_path: str,
        collection_id: str = None,
    ) -> File:
        """Create a new file record and save file to storage"""

        # Read file content
        file_content = await upload_file.read()
        file_size = len(file_content)

        # Calculate checksum
        checksum = FileCRUD.calculate_file_checksum(file_content)

        # Check for duplicates
        existing_file = await FileCRUD.get_file_by_checksum(db, checksum, user_id)
        if existing_file:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"File already exists: {existing_file.original_filename}",
            )

        # Detect MIME type
        mime_type = magic.from_buffer(file_content, mime=True)

        # Detect file type
        file_type = FileCRUD.detect_file_type(upload_file.filename, mime_type)

        # Get or create collection
        if not collection_id:
            collection_id = await FileCRUD.get_or_create_default_collection(db, user_id)

        # Generate unique filename
        unique_filename = f"{checksum[:16]}_{upload_file.filename}"
        file_path = os.path.join(storage_path, unique_filename)

        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)

        # Save file to storage
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file_content)

        # Create file metadata including checksum
        file_metadata = {
            "checksum": checksum,
            "upload_timestamp": datetime.utcnow().isoformat(),
            "original_size": file_size,
        }

        # Create file record using existing schema
        db_file = File(
            filename=unique_filename,
            original_filename=upload_file.filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            mime_type=mime_type,
            collection_id=collection_id,
            status=FileStatus.UPLOADED,
            file_metadata=file_metadata,
        )

        try:
            db.add(db_file)
            await db.commit()
            await db.refresh(db_file)
            return db_file
        except IntegrityError:
            await db.rollback()
            # Clean up file if database operation fails
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create file record",
            )

    @staticmethod
    async def update_file_status(
        db: AsyncSession,
        file_id: str,
        status: FileStatus,
        error_message: Optional[str] = None,
        processing_metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[File]:
        """Update file processing status"""
        file = await FileCRUD.get_file_by_id(db, file_id)
        if not file:
            return None

        file.status = status
        if error_message:
            file.error_message = error_message
        if processing_metadata:
            # Store in file_metadata field
            if file.file_metadata:
                file.file_metadata.update(processing_metadata)
            else:
                file.file_metadata = processing_metadata

        if status == FileStatus.PROCESSING:
            file.processing_started_at = datetime.utcnow()
        elif status in [FileStatus.PROCESSED, FileStatus.FAILED]:
            file.processing_completed_at = datetime.utcnow()

        await db.commit()
        await db.refresh(file)
        return file

    @staticmethod
    async def update_extracted_text(
        db: AsyncSession, file_id: str, extracted_text: str
    ) -> Optional[File]:
        """Update file with extracted text length"""
        file = await FileCRUD.get_file_by_id(db, file_id)
        if not file:
            return None

        file.extracted_text_length = len(extracted_text)

        # Store text length in metadata
        if file.file_metadata:
            file.file_metadata["extracted_text_length"] = len(extracted_text)
        else:
            file.file_metadata = {"extracted_text_length": len(extracted_text)}

        await db.commit()
        await db.refresh(file)
        return file

    @staticmethod
    async def delete_file(db: AsyncSession, file_id: str, user_id: str) -> bool:
        """Delete file record and file from storage"""
        file = await FileCRUD.get_file_by_id(db, file_id, user_id)
        if not file:
            return False

        # Delete file from storage
        if os.path.exists(file.file_path):
            os.remove(file.file_path)

        # Delete file record
        await db.delete(file)
        await db.commit()
        return True

    @staticmethod
    async def get_file_stats(db: AsyncSession, user_id: str) -> Dict[str, Any]:
        """Get file statistics for user"""
        from sqlalchemy import case, func

        from backend.common.database.models import Collection

        # Get file counts by status
        status_counts = await db.execute(
            select(File.status, func.count(File.id).label("count"))
            .join(Collection)
            .filter(Collection.owner_id == user_id)
            .group_by(File.status)
        )

        # Get file counts by type
        type_counts = await db.execute(
            select(File.file_type, func.count(File.id).label("count"))
            .join(Collection)
            .filter(Collection.owner_id == user_id)
            .group_by(File.file_type)
        )

        # Get total size
        total_size = await db.execute(
            select(func.sum(File.file_size)).join(Collection).filter(Collection.owner_id == user_id)
        )

        # Get total chunks
        total_chunks = await db.execute(
            select(func.sum(File.total_chunks))
            .join(Collection)
            .filter(Collection.owner_id == user_id)
        )

        return {
            "status_counts": {row.status: row.count for row in status_counts},
            "type_counts": {row.file_type: row.count for row in type_counts},
            "total_size_bytes": total_size.scalar() or 0,
            "total_chunks": total_chunks.scalar() or 0,
        }


class FileChunkCRUD:
    """File chunk CRUD operations"""

    @staticmethod
    async def create_chunks(
        db: AsyncSession,
        file_id: str,
        chunks: List[Dict[str, Any]],
        chunking_strategy: ChunkingStrategy,
    ) -> List[FileChunk]:
        """Create chunk records for a file"""
        chunk_records = []

        for i, chunk_data in enumerate(chunks):
            chunk_record = FileChunk(
                file_id=file_id,
                chunk_index=i,
                content=chunk_data["text"],
                content_length=len(chunk_data["text"]),
                embedding_model="text-embedding-3-small",  # Default model
                page_number=chunk_data.get("metadata", {}).get("page_number"),
                section_title=chunk_data.get("metadata", {}).get("section_title"),
                chunk_metadata={
                    "chunking_strategy": chunking_strategy.value,
                    "chunk_size": chunk_data.get("chunk_size"),
                    "overlap": chunk_data.get("overlap"),
                    **chunk_data.get("metadata", {}),
                },
            )
            chunk_records.append(chunk_record)

        db.add_all(chunk_records)
        await db.commit()

        # Refresh all records
        for chunk in chunk_records:
            await db.refresh(chunk)

        # Update file total chunks count
        file = await FileCRUD.get_file_by_id(db, file_id)
        if file:
            file.total_chunks = len(chunk_records)
            await db.commit()

        return chunk_records

    @staticmethod
    async def get_chunks_by_file(db: AsyncSession, file_id: str) -> List[FileChunk]:
        """Get all chunks for a file"""
        result = await db.execute(
            select(FileChunk).filter(FileChunk.file_id == file_id).order_by(FileChunk.chunk_index)
        )
        return result.scalars().all()

    @staticmethod
    async def update_chunk_embedding(
        db: AsyncSession,
        chunk_id: str,
        embedding_vector: List[float],
        embedding_model: str,
        vector_id: Optional[str] = None,
    ) -> Optional[FileChunk]:
        """Update chunk with embedding information"""
        result = await db.execute(select(FileChunk).filter(FileChunk.id == chunk_id))
        chunk = result.scalar_one_or_none()

        if not chunk:
            return None

        chunk.embedding_model = embedding_model
        if vector_id:
            chunk.vector_id = vector_id

        # Store embedding info in metadata
        if chunk.chunk_metadata:
            chunk.chunk_metadata.update(
                {
                    "embedding_model": embedding_model,
                    "embedding_dimensions": len(embedding_vector),
                    "vector_id": vector_id,
                }
            )
        else:
            chunk.chunk_metadata = {
                "embedding_model": embedding_model,
                "embedding_dimensions": len(embedding_vector),
                "vector_id": vector_id,
            }

        await db.commit()
        await db.refresh(chunk)
        return chunk


class ProcessingJobCRUD:
    """Processing job CRUD operations"""

    @staticmethod
    async def create_job(
        db: AsyncSession, file_id: str, job_type: str, job_config: Optional[Dict[str, Any]] = None
    ) -> ProcessingJob:
        """Create a new processing job"""
        job = ProcessingJob(
            file_id=file_id,
            job_type=job_type,
            status=FileStatus.UPLOADED,
            job_config=job_config or {},
            progress_percentage=0,
        )

        db.add(job)
        await db.commit()
        await db.refresh(job)
        return job

    @staticmethod
    async def update_job_progress(
        db: AsyncSession, job_id: str, progress_percentage: int, current_step: Optional[str] = None
    ) -> Optional[ProcessingJob]:
        """Update job progress"""
        result = await db.execute(select(ProcessingJob).filter(ProcessingJob.id == job_id))
        job = result.scalar_one_or_none()

        if not job:
            return None

        job.progress_percentage = progress_percentage
        if current_step:
            job.current_step = current_step

        await db.commit()
        await db.refresh(job)
        return job

    @staticmethod
    async def complete_job(
        db: AsyncSession, job_id: str, status: FileStatus, error_message: Optional[str] = None
    ) -> Optional[ProcessingJob]:
        """Complete a processing job"""
        result = await db.execute(select(ProcessingJob).filter(ProcessingJob.id == job_id))
        job = result.scalar_one_or_none()

        if not job:
            return None

        job.status = status
        job.completed_at = datetime.utcnow()
        job.progress_percentage = 100 if status == FileStatus.PROCESSED else job.progress_percentage

        if error_message:
            job.error_message = error_message

        await db.commit()
        await db.refresh(job)
        return job
