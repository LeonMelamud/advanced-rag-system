"""
File Service API Routes
Handles file upload, processing, and management endpoints
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import List, Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.api import BaseResponse, DataResponse
from backend.common.auth import UserContext, get_current_user
from backend.common.database import get_db, get_db_session
from backend.common.health_checks import check_openai_api, check_qdrant
from backend.file_service.app.chunking.chunker import ChunkingService
from backend.file_service.app.core.config import get_settings
from backend.file_service.app.crud.file import FileChunkCRUD, FileCRUD, ProcessingJobCRUD
from backend.file_service.app.embedding.embedder import EmbeddingService
from backend.file_service.app.models.file import ChunkingStrategy
from backend.file_service.app.models.file import File as FileModel
from backend.file_service.app.models.file import FileStatus, FileType
from backend.file_service.app.processing.text_extractor import TextExtractionService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
text_extraction_service = TextExtractionService()
chunking_service = ChunkingService()

# Initialize embedding service (will use mock if no OpenAI key)
try:
    embedding_service = EmbeddingService(provider="openai")
except ValueError:
    # Fallback to mock embedder if no OpenAI key
    embedding_service = EmbeddingService(provider="mock")


async def process_file_pipeline(
    file_id: str,
    chunking_strategy: ChunkingStrategy = ChunkingStrategy.RECURSIVE,
    chunk_size: int = 1000,
    chunk_overlap: int = 100,
):
    """Background task to process file through the complete pipeline"""
    print(f"BACKGROUND TASK STARTED for file {file_id}")
    logger.info(f"Starting background processing for file {file_id}")

    # Create a new database session for the background task
    from backend.common.database import get_db_session

    async with get_db_session() as db:
        try:
            # Get file record
            file_record = await FileCRUD.get_file_by_id(db, file_id)
            if not file_record:
                return

            # Update status to processing
            await FileCRUD.update_file_status(db, file_id, FileStatus.PROCESSING)

            # Step 1: Text Extraction
            extraction_result = await text_extraction_service.extract_text(
                file_record.file_path, file_record.file_type
            )

            if not extraction_result["success"]:
                await FileCRUD.update_file_status(
                    db,
                    file_id,
                    FileStatus.FAILED,
                    error_message=f"Text extraction failed: {extraction_result['error']}",
                )
                return

            # Update file with extracted text
            await FileCRUD.update_extracted_text(db, file_id, extraction_result["text"])

            # Step 2: Text Chunking
            chunks = chunking_service.chunk_text(
                text=extraction_result["text"],
                strategy=chunking_strategy,
                chunk_size=chunk_size,
                overlap=chunk_overlap,
                metadata=extraction_result["metadata"],
            )

            # Create chunk records
            chunk_records = await FileChunkCRUD.create_chunks(
                db, file_id, chunks, chunking_strategy
            )

            # Step 3: Generate Embeddings
            logger.info(f"Starting embedding generation for {len(chunks)} chunks")
            enriched_chunks = await embedding_service.embed_chunks(chunks)
            logger.info(f"Embedding generation completed, got {len(enriched_chunks)} results")

            # Update chunks with embeddings and collect successful embeddings
            successful_embeddings = []
            successful_chunks = []

            for i, chunk_record in enumerate(chunk_records):
                logger.info(f"Processing chunk {i}: enriched_chunks length={len(enriched_chunks)}")
                if i < len(enriched_chunks):
                    logger.info(f"Chunk {i} enriched data keys: {list(enriched_chunks[i].keys())}")
                    logger.info(f"Chunk {i} success value: {enriched_chunks[i].get('success')}")
                    logger.info(f"Chunk {i} embedding present: {'embedding' in enriched_chunks[i]}")
                    if enriched_chunks[i].get("success"):
                        # Update chunk record with embedding info
                        await FileChunkCRUD.update_chunk_embedding(
                            db,
                            chunk_record.id,
                            enriched_chunks[i]["embedding"],
                            enriched_chunks[i]["embedding_model"],
                        )

                        # Collect for vector storage
                        successful_embeddings.append(enriched_chunks[i]["embedding"])
                        successful_chunks.append(chunk_record)
                        logger.info(f"Added chunk {i} to successful embeddings")
                    else:
                        logger.warning(
                            f"Chunk {i} embedding failed or missing success flag: {enriched_chunks[i].get('success')}"
                        )
                        logger.warning(f"Chunk {i} error: {enriched_chunks[i].get('error')}")
                else:
                    logger.warning(f"Chunk {i} embedding failed or missing")

            logger.info(
                f"Embedding processing complete: {len(successful_embeddings)} successful embeddings"
            )

            # Step 4: Store Embeddings in Vector Database
            logger.info(
                f"Vector storage check: successful_embeddings={len(successful_embeddings)}, successful_chunks={len(successful_chunks)}"
            )

            if successful_embeddings and successful_chunks:
                try:
                    from ..core.vector_integration import get_file_vector_service

                    vector_service = await get_file_vector_service()

                    # Use default collection if file doesn't have one assigned
                    collection_id = file_record.collection_id or "default_collection"

                    logger.info(
                        f"Attempting to store {len(successful_embeddings)} embeddings in collection {collection_id}"
                    )

                    vector_ids = await vector_service.store_chunk_embeddings(
                        chunks=successful_chunks,
                        embeddings=successful_embeddings,
                        collection_id=collection_id,
                    )

                    # Update chunk records with vector IDs
                    for chunk_record, vector_id in zip(successful_chunks, vector_ids):
                        await FileChunkCRUD.update_chunk_embedding(
                            db,
                            chunk_record.id,
                            None,  # Embedding already stored in vector DB
                            chunk_record.embedding_model,  # Keep existing model
                            vector_id=vector_id,
                        )

                    logger.info(
                        f"Successfully stored {len(vector_ids)} embeddings in vector database for file {file_id} in collection {collection_id}"
                    )

                except Exception as e:
                    logger.error(
                        f"Failed to store embeddings in vector database: {e}", exc_info=True
                    )
                    # Don't fail the entire pipeline for vector storage issues
                    # The embeddings are still stored in the database
            else:
                logger.warning(
                    f"Skipping vector storage: successful_embeddings={len(successful_embeddings)}, successful_chunks={len(successful_chunks)}"
                )

            # Update file status to processed
            processing_metadata = {
                "extraction_metadata": extraction_result["metadata"],
                "chunking_strategy": chunking_strategy.value,
                "chunk_count": len(chunks),
                "successful_embeddings": len(successful_embeddings),
                "embedding_model": embedding_service.get_model_info(),
                "vector_storage": len(successful_embeddings) > 0,
            }

            await FileCRUD.update_file_status(
                db, file_id, FileStatus.PROCESSED, processing_metadata=processing_metadata
            )

        except Exception as e:
            # Update file status to failed
            await FileCRUD.update_file_status(
                db,
                file_id,
                FileStatus.FAILED,
                error_message=f"Processing pipeline failed: {str(e)}",
            )


@router.get("/", response_model=DataResponse[List[dict]])
async def list_files(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[FileStatus] = Query(None),
    file_type: Optional[FileType] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    """List files for the current user"""
    files = await FileCRUD.get_files_by_user(
        db, current_user.user_id, skip, limit, status, file_type
    )

    file_data = []
    for file in files:
        file_data.append(
            {
                "id": file.id,
                "filename": file.original_filename,
                "file_type": file.file_type,
                "file_size": file.file_size,
                "status": file.status,
                "created_at": file.created_at,
                "processing_started_at": file.processing_started_at,
                "processing_completed_at": file.processing_completed_at,
                "text_length": file.extracted_text_length,
                "total_chunks": file.total_chunks,
                "chunking_strategy": (
                    file.file_metadata.get("chunking_strategy") if file.file_metadata else None
                ),
                "error_message": file.error_message,
            }
        )

    return DataResponse(success=True, message=f"Retrieved {len(file_data)} files", data=file_data)


@router.post("/upload", response_model=DataResponse[dict])
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    chunking_strategy: ChunkingStrategy = Query(ChunkingStrategy.RECURSIVE),
    chunk_size: int = Query(1000, ge=100, le=5000),
    chunk_overlap: int = Query(100, ge=0, le=500),
    auto_process: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    """Upload a file and optionally start processing"""
    settings = get_settings()

    # Validate file size
    if file.size and file.size > settings.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.max_file_size_mb}MB",
        )

    # Validate file extension
    file_extension = f".{file.filename.split('.')[-1].lower()}" if "." in file.filename else ""
    if file_extension not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Supported types: {', '.join(settings.allowed_extensions)}",
        )

    try:
        # Create file record and save to storage
        file_record = await FileCRUD.create_file(db, file, current_user.user_id, settings.temp_dir)

        response_data = {
            "id": file_record.id,
            "filename": file_record.original_filename,
            "file_type": file_record.file_type,
            "file_size": file_record.file_size,
            "status": file_record.status,
            "checksum": (
                file_record.file_metadata.get("checksum") if file_record.file_metadata else None
            ),
            "created_at": file_record.created_at,
        }

        # Start background processing if requested
        if auto_process:
            background_tasks.add_task(
                process_file_pipeline,
                file_record.id,
                chunking_strategy,
                chunk_size,
                chunk_overlap,
            )
            response_data["processing_started"] = True

        return DataResponse(success=True, message="File uploaded successfully", data=response_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}",
        )


@router.get("/{file_id}", response_model=DataResponse[dict])
async def get_file(
    file_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    """Get file information by ID"""
    file_record = await FileCRUD.get_file_by_id(db, file_id, current_user.user_id)

    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    file_data = {
        "id": file_record.id,
        "filename": file_record.original_filename,
        "file_type": file_record.file_type,
        "file_size": file_record.file_size,
        "mime_type": file_record.mime_type,
        "status": file_record.status,
        "checksum": (
            file_record.file_metadata.get("checksum") if file_record.file_metadata else None
        ),
        "created_at": file_record.created_at,
        "processing_started_at": file_record.processing_started_at,
        "processing_completed_at": file_record.processing_completed_at,
        "text_length": file_record.extracted_text_length,
        "total_chunks": file_record.total_chunks,
        "chunking_strategy": (
            file_record.file_metadata.get("chunking_strategy")
            if file_record.file_metadata
            else None
        ),
        "file_metadata": file_record.file_metadata,
        "error_message": file_record.error_message,
    }

    return DataResponse(success=True, message="File retrieved successfully", data=file_data)


@router.get("/{file_id}/chunks", response_model=DataResponse[List[dict]])
async def get_file_chunks(
    file_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    """Get chunks for a file"""
    # Verify file ownership
    file_record = await FileCRUD.get_file_by_id(db, file_id, current_user.user_id)
    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    chunks = await FileChunkCRUD.get_chunks_by_file(db, file_id)

    # Apply pagination
    paginated_chunks = chunks[skip : skip + limit]

    chunk_data = []
    for chunk in paginated_chunks:
        chunk_data.append(
            {
                "id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "content_length": chunk.content_length,
                "page_number": chunk.page_number,
                "section_title": chunk.section_title,
                "vector_id": chunk.vector_id,
                "embedding_model": chunk.embedding_model,
                "chunk_metadata": chunk.chunk_metadata,
                "created_at": chunk.created_at,
            }
        )

    return DataResponse(
        success=True,
        message=f"Retrieved {len(chunk_data)} chunks (total: {len(chunks)})",
        data=chunk_data,
    )


@router.post("/{file_id}/process", response_model=BaseResponse)
async def process_file(
    file_id: str,
    background_tasks: BackgroundTasks,
    chunking_strategy: ChunkingStrategy = Query(ChunkingStrategy.RECURSIVE),
    chunk_size: int = Query(1000, ge=100, le=5000),
    chunk_overlap: int = Query(100, ge=0, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    """Manually trigger file processing"""
    file_record = await FileCRUD.get_file_by_id(db, file_id, current_user.user_id)

    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    if file_record.status == FileStatus.PROCESSING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="File is already being processed"
        )

    if file_record.status == FileStatus.PROCESSED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="File has already been processed"
        )

    # Start background processing
    background_tasks.add_task(
        process_file_pipeline, file_id, chunking_strategy, chunk_size, chunk_overlap
    )

    return BaseResponse(success=True, message="File processing started")


@router.delete("/{file_id}", response_model=BaseResponse)
async def delete_file(
    file_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    """Delete a file"""
    success = await FileCRUD.delete_file(db, file_id, current_user.user_id)

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    return BaseResponse(success=True, message="File deleted successfully")


@router.get("/stats/summary", response_model=DataResponse[dict])
async def get_file_stats(
    db: AsyncSession = Depends(get_db), current_user: UserContext = Depends(get_current_user)
):
    """Get file statistics for the current user"""
    stats = await FileCRUD.get_file_stats(db, current_user.user_id)

    return DataResponse(success=True, message="File statistics retrieved successfully", data=stats)


@router.get("/config/info", response_model=DataResponse[dict])
async def get_service_info():
    """Get file service configuration and capabilities"""
    settings = get_settings()

    info = {
        "service_name": "File Service",
        "version": "1.0.0",
        "max_file_size_mb": settings.max_file_size_mb,
        "allowed_extensions": settings.allowed_extensions,
        "supported_file_types": [ft.value for ft in FileType],
        "supported_chunking_strategies": [cs.value for cs in ChunkingStrategy],
        "default_chunk_size": settings.default_chunk_size,
        "default_chunk_overlap": settings.default_chunk_overlap,
        "embedding_model": embedding_service.get_model_info(),
        "text_extraction_capabilities": text_extraction_service.get_supported_file_types(),
        "vector_database": "Qdrant",
        "capabilities": [
            "file_upload",
            "text_extraction",
            "chunking",
            "embedding_generation",
            "vector_storage",
            "similarity_search",
        ],
    }

    return DataResponse(
        success=True, message="Service information retrieved successfully", data=info
    )


@router.post("/search/similar", response_model=DataResponse[List[dict]])
async def search_similar_chunks(
    query: str,
    collection_id: str = Query(..., description="Collection ID to search in"),
    limit: int = Query(10, ge=1, le=50, description="Number of results to return"),
    score_threshold: float = Query(0.0, ge=0.0, le=1.0, description="Minimum similarity score"),
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    """Search for similar chunks using text query"""
    try:
        # Generate embedding for query
        embedding_result = await embedding_service.embed_text(query)

        if not embedding_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to generate query embedding: {embedding_result['error']}",
            )

        # Search vector database
        from ..core.vector_integration import get_file_vector_service

        vector_service = await get_file_vector_service()

        results = await vector_service.search_similar_chunks(
            query_embedding=embedding_result["embedding"],
            collection_id=collection_id,
            limit=limit,
            score_threshold=score_threshold,
        )

        # Format results
        search_results = []
        for result in results:
            search_results.append(
                {
                    "chunk_id": result.payload.get("chunk_id"),
                    "file_id": result.payload.get("file_id"),
                    "content": result.payload.get("content"),
                    "similarity_score": result.score,
                    "chunk_index": result.payload.get("chunk_index"),
                    "page_number": result.payload.get("page_number"),
                    "section_title": result.payload.get("section_title"),
                    "content_length": result.payload.get("content_length"),
                }
            )

        return DataResponse(
            success=True, message=f"Found {len(search_results)} similar chunks", data=search_results
        )

    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vector search failed: {str(e)}",
        )


@router.get("/collections/{collection_id}/stats", response_model=DataResponse[dict])
async def get_collection_vector_stats(
    collection_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    """Get vector database statistics for a collection"""
    try:
        from ..core.vector_integration import get_file_vector_service

        vector_service = await get_file_vector_service()

        stats = await vector_service.get_collection_stats(collection_id)

        return DataResponse(
            success=True, message="Collection vector statistics retrieved successfully", data=stats
        )

    except Exception as e:
        logger.error(f"Failed to get collection stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get collection stats: {str(e)}",
        )


@router.get("/vector/collections", response_model=DataResponse[List[str]])
async def list_vector_collections(
    db: AsyncSession = Depends(get_db), current_user: UserContext = Depends(get_current_user)
):
    """List all vector database collections"""
    try:
        from ..core.vector_integration import get_file_vector_service

        vector_service = await get_file_vector_service()

        collections = await vector_service.list_collections()

        return DataResponse(
            success=True,
            message=f"Retrieved {len(collections)} vector collections",
            data=collections,
        )

    except Exception as e:
        logger.error(f"Failed to list vector collections: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list vector collections: {str(e)}",
        )


@router.get("/health/detailed", response_model=DataResponse[dict])
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check including vector database status"""
    try:
        from ..core.vector_integration import get_file_vector_service

        settings = get_settings()
        health_status = {
            "service": "File Service",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "dependencies": {},
        }

        # Check Qdrant
        try:
            qdrant_status = await check_qdrant(settings)
            health_status["dependencies"]["qdrant"] = qdrant_status
        except Exception as e:
            health_status["dependencies"]["qdrant"] = {"status": "unhealthy", "error": str(e)}

        # Check OpenAI API
        try:
            openai_status = await check_openai_api(settings)
            health_status["dependencies"]["openai"] = openai_status
        except Exception as e:
            health_status["dependencies"]["openai"] = {"status": "unhealthy", "error": str(e)}

        # Check vector service
        try:
            vector_service = await get_file_vector_service()
            collections = await vector_service.list_collections()
            health_status["dependencies"]["vector_service"] = {
                "status": "healthy",
                "collections_count": len(collections),
                "collections": collections,
            }
        except Exception as e:
            health_status["dependencies"]["vector_service"] = {
                "status": "unhealthy",
                "error": str(e),
            }

        # Determine overall status
        unhealthy_deps = [
            dep
            for dep, status in health_status["dependencies"].items()
            if status.get("status") != "healthy"
        ]

        if unhealthy_deps:
            health_status["status"] = "degraded"
            health_status["unhealthy_dependencies"] = unhealthy_deps

        return DataResponse(
            success=True, message="Detailed health check completed", data=health_status
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}",
        )
