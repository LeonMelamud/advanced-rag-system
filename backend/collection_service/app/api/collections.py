"""
Collection Management API Endpoints
Handles collection CRUD operations and access control
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.auth import UserContext, get_current_user

# Import shared components
from ..core.database import get_db
from ..crud.collection import CollectionAccessCRUD, CollectionCRUD
from ..models.collection import AccessLevel, CollectionStatus

# Import service-specific components
from ..models.schemas import (
    CollectionAccessCreate,
    CollectionAccessResponse,
    CollectionAccessUpdate,
    CollectionConfig,
    CollectionCreate,
    CollectionListResponse,
    CollectionResponse,
    CollectionStats,
    CollectionUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_collection(
    collection_data: CollectionCreate,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new collection"""
    try:
        collection = await CollectionCRUD.create_collection(
            db=db, owner_id=current_user.user_id, collection_data=collection_data
        )

        logger.info(f"User {current_user.user_id} created collection {collection.id}")
        return CollectionResponse.from_orm(collection)

    except Exception as e:
        logger.error(f"Error creating collection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create collection"
        )


@router.get("/", response_model=CollectionListResponse)
async def list_collections(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status_filter: Optional[CollectionStatus] = Query(default=None, alias="status"),
    search: Optional[str] = Query(default=None, max_length=255),
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List collections accessible to the current user"""
    try:
        collections = await CollectionCRUD.get_user_collections(
            db=db,
            user_id=current_user.user_id,
            limit=limit,
            offset=offset,
            status=status_filter,
            search=search,
        )

        logger.info(f"Retrieved {len(collections)} collections")

        # Get total count for pagination
        total_collections = await CollectionCRUD.get_user_collections(
            db=db,
            user_id=current_user.user_id,
            limit=1000000,  # Large number to get all
            offset=0,
            status=status_filter,
            search=search,
        )

        total_count = len(total_collections)
        has_more = offset + limit < total_count

        collection_responses = []
        for c in collections:
            logger.info(f"Processing collection {c.id}, settings: {c.settings}")
            collection_responses.append(
                CollectionResponse(
                    id=c.id,
                    name=c.name,
                    description=c.description,
                    owner_id=c.owner_id,
                    status=c.status,
                    is_public=c.is_public,
                    vector_collection_name=c.vector_collection_name,
                    embedding_model=c.embedding_model,
                    embedding_dimensions=c.embedding_dimensions,
                    chunking_strategy=c.chunking_strategy,
                    chunk_size=c.chunk_size,
                    chunk_overlap=c.chunk_overlap,
                    settings=c.settings or {},
                    document_count=c.document_count,
                    total_chunks=c.total_chunks,
                    created_at=c.created_at,
                    updated_at=c.updated_at,
                )
            )

        return CollectionListResponse(
            collections=collection_responses, total_count=total_count, has_more=has_more
        )

    except Exception as e:
        logger.error(f"Error listing collections: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list collections"
        )


@router.get("/{collection_id}", response_model=CollectionResponse)
async def get_collection(
    collection_id: UUID,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific collection"""
    try:
        collection = await CollectionCRUD.get_collection(
            db=db, collection_id=collection_id, user_id=current_user.user_id
        )

        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found or access denied",
            )

        return CollectionResponse(
            id=collection.id,
            name=collection.name,
            description=collection.description,
            owner_id=collection.owner_id,
            status=collection.status,
            is_public=collection.is_public,
            vector_collection_name=collection.vector_collection_name,
            embedding_model=collection.embedding_model,
            embedding_dimensions=collection.embedding_dimensions,
            chunking_strategy=collection.chunking_strategy,
            chunk_size=collection.chunk_size,
            chunk_overlap=collection.chunk_overlap,
            settings=collection.settings or {},
            document_count=collection.document_count,
            total_chunks=collection.total_chunks,
            created_at=collection.created_at,
            updated_at=collection.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting collection {collection_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get collection"
        )


@router.put("/{collection_id}", response_model=CollectionResponse)
async def update_collection(
    collection_id: UUID,
    updates: CollectionUpdate,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a collection"""
    try:
        collection = await CollectionCRUD.update_collection(
            db=db, collection_id=collection_id, user_id=current_user.user_id, updates=updates
        )

        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found or insufficient permissions",
            )

        logger.info(f"User {current_user.user_id} updated collection {collection_id}")
        return CollectionResponse(
            id=collection.id,
            name=collection.name,
            description=collection.description,
            owner_id=collection.owner_id,
            status=collection.status,
            is_public=collection.is_public,
            vector_collection_name=collection.vector_collection_name,
            embedding_model=collection.embedding_model,
            embedding_dimensions=collection.embedding_dimensions,
            chunking_strategy=collection.chunking_strategy,
            chunk_size=collection.chunk_size,
            chunk_overlap=collection.chunk_overlap,
            settings=collection.settings or {},
            document_count=collection.document_count,
            total_chunks=collection.total_chunks,
            created_at=collection.created_at,
            updated_at=collection.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating collection {collection_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update collection"
        )


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(
    collection_id: UUID,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete (archive) a collection"""
    try:
        success = await CollectionCRUD.delete_collection(
            db=db, collection_id=collection_id, user_id=current_user.user_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found or insufficient permissions",
            )

        logger.info(f"User {current_user.user_id} deleted collection {collection_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting collection {collection_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete collection"
        )


@router.get("/{collection_id}/stats", response_model=CollectionStats)
async def get_collection_stats(
    collection_id: UUID,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get collection statistics"""
    try:
        collection = await CollectionCRUD.get_collection(
            db=db, collection_id=collection_id, user_id=current_user.user_id
        )

        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found or access denied",
            )

        return CollectionStats(
            collection_id=collection_id,
            document_count=collection.document_count,
            total_chunks=collection.total_chunks,
            embedding_model=collection.embedding_model,
            chunking_strategy=collection.chunking_strategy,
            chunk_size=collection.chunk_size,
            chunk_overlap=collection.chunk_overlap,
            created_at=collection.created_at,
            updated_at=collection.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting collection stats {collection_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get collection statistics",
        )


@router.get("/{collection_id}/config", response_model=CollectionConfig)
async def get_collection_config(
    collection_id: UUID,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get collection configuration"""
    try:
        collection = await CollectionCRUD.get_collection(
            db=db, collection_id=collection_id, user_id=current_user.user_id
        )

        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found or access denied",
            )

        return CollectionConfig(
            embedding_model=collection.embedding_model,
            embedding_dimensions=collection.embedding_dimensions,
            chunking_strategy=collection.chunking_strategy,
            chunk_size=collection.chunk_size,
            chunk_overlap=collection.chunk_overlap,
            settings=collection.settings or {},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting collection config {collection_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get collection configuration",
        )


@router.post(
    "/{collection_id}/access",
    response_model=CollectionAccessResponse,
    status_code=status.HTTP_201_CREATED,
)
async def grant_collection_access(
    collection_id: UUID,
    access_data: CollectionAccessCreate,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Grant access to a collection (owner only)"""
    try:
        # Check if user is owner
        collection = await CollectionCRUD.get_collection(
            db=db, collection_id=collection_id, user_id=current_user.user_id
        )

        if not collection or collection.owner_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found or insufficient permissions",
            )

        access = await CollectionAccessCRUD.grant_access(
            db=db, collection_id=collection_id, access_data=access_data
        )

        logger.info(
            f"User {current_user.user_id} granted access to collection {collection_id} for user {access_data.user_id}"
        )
        return CollectionAccessResponse.from_orm(access)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error granting collection access: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to grant collection access",
        )


@router.get("/{collection_id}/access", response_model=List[CollectionAccessResponse])
async def list_collection_access(
    collection_id: UUID,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List collection access permissions (owner only)"""
    try:
        # Check if user is owner
        collection = await CollectionCRUD.get_collection(
            db=db, collection_id=collection_id, user_id=current_user.user_id
        )

        if not collection or collection.owner_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found or insufficient permissions",
            )

        access_list = await CollectionAccessCRUD.list_collection_access(
            db=db, collection_id=collection_id
        )

        return [CollectionAccessResponse.from_orm(access) for access in access_list]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing collection access: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list collection access",
        )


@router.put("/{collection_id}/access/{user_id}", response_model=CollectionAccessResponse)
async def update_collection_access(
    collection_id: UUID,
    user_id: UUID,
    updates: CollectionAccessUpdate,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update collection access permissions (owner only)"""
    try:
        # Check if user is owner
        collection = await CollectionCRUD.get_collection(
            db=db, collection_id=collection_id, user_id=current_user.user_id
        )

        if not collection or collection.owner_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found or insufficient permissions",
            )

        access = await CollectionAccessCRUD.update_access(
            db=db, collection_id=collection_id, user_id=user_id, updates=updates
        )

        if not access:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Access record not found"
            )

        logger.info(
            f"User {current_user.user_id} updated access for collection {collection_id} user {user_id}"
        )
        return CollectionAccessResponse.from_orm(access)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating collection access: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update collection access",
        )


@router.delete("/{collection_id}/access/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_collection_access(
    collection_id: UUID,
    user_id: UUID,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke collection access (owner only)"""
    try:
        # Check if user is owner
        collection = await CollectionCRUD.get_collection(
            db=db, collection_id=collection_id, user_id=current_user.user_id
        )

        if not collection or collection.owner_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found or insufficient permissions",
            )

        success = await CollectionAccessCRUD.revoke_access(
            db=db, collection_id=collection_id, user_id=user_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Access record not found"
            )

        logger.info(
            f"User {current_user.user_id} revoked access for collection {collection_id} user {user_id}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking collection access: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke collection access",
        )
