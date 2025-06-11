"""
Collection Service CRUD Operations
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_, delete, desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.collection import (
    AccessLevel,
    Collection,
    CollectionAccess,
    CollectionStatus,
    CollectionVersion,
)
from ..models.schemas import (
    CollectionAccessCreate,
    CollectionAccessUpdate,
    CollectionCreate,
    CollectionUpdate,
    CollectionVersionCreate,
)

logger = logging.getLogger(__name__)


class CollectionCRUD:
    """CRUD operations for collections"""

    @staticmethod
    async def create_collection(
        db: AsyncSession, owner_id: UUID, collection_data: CollectionCreate
    ) -> Collection:
        """Create a new collection"""
        try:
            # Generate unique vector collection name
            vector_collection_name = (
                f"collection_{collection_data.name.lower().replace(' ', '_')}_{str(owner_id)[:8]}"
            )

            collection = Collection(
                name=collection_data.name,
                description=collection_data.description,
                owner_id=owner_id,
                is_public=collection_data.is_public,
                vector_collection_name=vector_collection_name,
                embedding_model=collection_data.embedding_model,
                embedding_dimensions=collection_data.embedding_dimensions,
                chunking_strategy=collection_data.chunking_strategy,
                chunk_size=collection_data.chunk_size,
                chunk_overlap=collection_data.chunk_overlap,
                settings=collection_data.settings,
            )

            db.add(collection)
            await db.commit()
            await db.refresh(collection)

            # Create initial version
            await CollectionVersionCRUD.create_version(
                db=db,
                collection_id=collection.id,
                created_by=owner_id,
                version_data=CollectionVersionCreate(
                    description="Initial collection version",
                    changes={"action": "created", "initial_config": collection_data.dict()},
                ),
            )

            logger.info(f"Created collection {collection.id} for user {owner_id}")
            return collection

        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating collection: {e}")
            raise

    @staticmethod
    async def get_collection(
        db: AsyncSession, collection_id: UUID, user_id: Optional[UUID] = None
    ) -> Optional[Collection]:
        """Get a collection by ID with optional access check"""
        try:
            query = select(Collection).where(Collection.id == collection_id)

            # If user_id provided, check access
            if user_id:
                # User can access if they own it or have explicit access
                access_query = select(CollectionAccess).where(
                    and_(
                        CollectionAccess.collection_id == collection_id,
                        CollectionAccess.user_id == user_id,
                    )
                )
                access_result = await db.execute(access_query)
                access = access_result.scalar_one_or_none()

                # Check if user is owner or has access
                collection_query = select(Collection).where(
                    and_(
                        Collection.id == collection_id,
                        or_(
                            Collection.owner_id == user_id,
                            access.id.isnot(None) if access else False,
                        ),
                    )
                )
                result = await db.execute(collection_query)
            else:
                result = await db.execute(query)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting collection {collection_id}: {e}")
            raise

    @staticmethod
    async def get_user_collections(
        db: AsyncSession,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
        status: Optional[CollectionStatus] = None,
        search: Optional[str] = None,
    ) -> List[Collection]:
        """Get collections accessible to a user"""
        try:
            # Get collections where user is owner or has access
            query = (
                select(Collection)
                .join(
                    CollectionAccess,
                    and_(
                        CollectionAccess.collection_id == Collection.id,
                        CollectionAccess.user_id == user_id,
                    ),
                    isouter=True,
                )
                .where(or_(Collection.owner_id == user_id, CollectionAccess.user_id == user_id))
            )

            # Apply filters
            if status:
                query = query.where(Collection.status == status)

            if search:
                search_pattern = f"%{search}%"
                query = query.where(
                    or_(
                        Collection.name.ilike(search_pattern),
                        Collection.description.ilike(search_pattern),
                    )
                )

            query = query.order_by(desc(Collection.updated_at)).limit(limit).offset(offset)

            result = await db.execute(query)
            return result.scalars().unique().all()

        except Exception as e:
            logger.error(f"Error getting user collections for {user_id}: {e}")
            raise

    @staticmethod
    async def update_collection(
        db: AsyncSession, collection_id: UUID, user_id: UUID, updates: CollectionUpdate
    ) -> Optional[Collection]:
        """Update a collection"""
        try:
            # Check if user has write access
            collection = await CollectionCRUD.get_collection(db, collection_id, user_id)
            if not collection:
                return None

            # Check write permissions
            if collection.owner_id != user_id:
                access = await CollectionAccessCRUD.get_user_access(db, collection_id, user_id)
                if not access or not access.can_write:
                    return None

            # Build update dictionary
            update_data = {}
            changes = {}

            for field, value in updates.dict(exclude_unset=True).items():
                if value is not None:
                    update_data[field] = value
                    changes[field] = {"old": getattr(collection, field), "new": value}

            if not update_data:
                return collection

            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow()

            # Update collection
            query = update(Collection).where(Collection.id == collection_id).values(**update_data)
            await db.execute(query)

            # Create version for changes
            await CollectionVersionCRUD.create_version(
                db=db,
                collection_id=collection_id,
                created_by=user_id,
                version_data=CollectionVersionCreate(
                    description=f"Updated collection: {', '.join(changes.keys())}", changes=changes
                ),
            )

            await db.commit()

            # Return updated collection
            return await CollectionCRUD.get_collection(db, collection_id, user_id)

        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating collection {collection_id}: {e}")
            raise

    @staticmethod
    async def delete_collection(db: AsyncSession, collection_id: UUID, user_id: UUID) -> bool:
        """Delete a collection (soft delete by marking as archived)"""
        try:
            # Check if user is owner
            collection = await CollectionCRUD.get_collection(db, collection_id, user_id)
            if not collection or collection.owner_id != user_id:
                return False

            # Soft delete by marking as archived
            query = (
                update(Collection)
                .where(Collection.id == collection_id)
                .values(status=CollectionStatus.ARCHIVED, updated_at=datetime.utcnow())
            )

            result = await db.execute(query)

            # Create version for deletion
            await CollectionVersionCRUD.create_version(
                db=db,
                collection_id=collection_id,
                created_by=user_id,
                version_data=CollectionVersionCreate(
                    description="Collection archived",
                    changes={"action": "archived", "status": "archived"},
                ),
            )

            await db.commit()

            return result.rowcount > 0

        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting collection {collection_id}: {e}")
            raise

    @staticmethod
    async def update_collection_stats(
        db: AsyncSession,
        collection_id: UUID,
        document_count: int,
        total_chunks: int,
    ) -> bool:
        """Update collection statistics"""
        try:
            query = (
                update(Collection)
                .where(Collection.id == collection_id)
                .values(
                    document_count=document_count,
                    total_chunks=total_chunks,
                    updated_at=datetime.utcnow(),
                )
            )

            result = await db.execute(query)
            await db.commit()

            return result.rowcount > 0

        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating collection stats {collection_id}: {e}")
            raise


class CollectionVersionCRUD:
    """CRUD operations for collection versions"""

    @staticmethod
    async def create_version(
        db: AsyncSession,
        collection_id: UUID,
        created_by: UUID,
        version_data: CollectionVersionCreate,
    ) -> CollectionVersion:
        """Create a new collection version"""
        try:
            # Get next version number
            version_query = select(func.max(CollectionVersion.version_number)).where(
                CollectionVersion.collection_id == collection_id
            )
            result = await db.execute(version_query)
            max_version = result.scalar() or 0
            next_version = max_version + 1

            # Get current collection configuration
            collection_query = select(Collection).where(Collection.id == collection_id)
            collection_result = await db.execute(collection_query)
            collection = collection_result.scalar_one()

            version = CollectionVersion(
                collection_id=collection_id,
                version_number=next_version,
                description=version_data.description,
                changes=version_data.changes,
                configuration_snapshot={
                    "embedding_model": collection.embedding_model,
                    "embedding_dimensions": collection.embedding_dimensions,
                    "chunking_strategy": collection.chunking_strategy,
                    "chunk_size": collection.chunk_size,
                    "chunk_overlap": collection.chunk_overlap,
                    "settings": collection.settings,
                },
                document_count=collection.document_count,
                total_chunks=collection.total_chunks,
                total_size_bytes=0,  # Default value since this field doesn't exist in main table
                created_by=created_by,
            )

            db.add(version)
            await db.commit()
            await db.refresh(version)

            logger.info(f"Created version {next_version} for collection {collection_id}")
            return version

        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating collection version: {e}")
            raise

    @staticmethod
    async def get_collection_versions(
        db: AsyncSession, collection_id: UUID, limit: int = 20, offset: int = 0
    ) -> List[CollectionVersion]:
        """Get versions for a collection"""
        try:
            query = (
                select(CollectionVersion)
                .where(CollectionVersion.collection_id == collection_id)
                .order_by(desc(CollectionVersion.version_number))
                .limit(limit)
                .offset(offset)
            )

            result = await db.execute(query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error getting collection versions for {collection_id}: {e}")
            raise


class CollectionAccessCRUD:
    """CRUD operations for collection access control"""

    @staticmethod
    async def grant_access(
        db: AsyncSession, collection_id: UUID, granted_by: UUID, access_data: CollectionAccessCreate
    ) -> CollectionAccess:
        """Grant access to a collection"""
        try:
            # Check if access already exists
            existing_query = select(CollectionAccess).where(
                and_(
                    CollectionAccess.collection_id == collection_id,
                    CollectionAccess.user_id == access_data.user_id,
                )
            )
            existing_result = await db.execute(existing_query)
            existing_access = existing_result.scalar_one_or_none()

            if existing_access:
                # Update existing access
                update_query = (
                    update(CollectionAccess)
                    .where(CollectionAccess.id == existing_access.id)
                    .values(
                        access_level=access_data.access_level,
                        can_read=access_data.can_read,
                        can_write=access_data.can_write,
                        can_delete=access_data.can_delete,
                        can_manage_access=access_data.can_manage_access,
                        expires_at=access_data.expires_at,
                        granted_by=granted_by,
                        granted_at=datetime.utcnow(),
                    )
                )
                await db.execute(update_query)
                await db.commit()

                # Return updated access
                updated_result = await db.execute(existing_query)
                return updated_result.scalar_one()
            else:
                # Create new access
                access = CollectionAccess(
                    collection_id=collection_id,
                    user_id=access_data.user_id,
                    access_level=access_data.access_level,
                    can_read=access_data.can_read,
                    can_write=access_data.can_write,
                    can_delete=access_data.can_delete,
                    can_manage_access=access_data.can_manage_access,
                    expires_at=access_data.expires_at,
                    granted_by=granted_by,
                )

                db.add(access)
                await db.commit()
                await db.refresh(access)

                logger.info(
                    f"Granted access to collection {collection_id} for user {access_data.user_id}"
                )
                return access

        except Exception as e:
            await db.rollback()
            logger.error(f"Error granting collection access: {e}")
            raise

    @staticmethod
    async def get_user_access(
        db: AsyncSession, collection_id: UUID, user_id: UUID
    ) -> Optional[CollectionAccess]:
        """Get user's access to a collection"""
        try:
            query = select(CollectionAccess).where(
                and_(
                    CollectionAccess.collection_id == collection_id,
                    CollectionAccess.user_id == user_id,
                )
            )

            result = await db.execute(query)
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting user access: {e}")
            raise

    @staticmethod
    async def get_collection_access_list(
        db: AsyncSession, collection_id: UUID
    ) -> List[CollectionAccess]:
        """Get all access entries for a collection"""
        try:
            query = (
                select(CollectionAccess)
                .where(CollectionAccess.collection_id == collection_id)
                .order_by(CollectionAccess.granted_at)
            )

            result = await db.execute(query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error getting collection access list: {e}")
            raise

    @staticmethod
    async def revoke_access(db: AsyncSession, collection_id: UUID, user_id: UUID) -> bool:
        """Revoke user's access to a collection"""
        try:
            query = delete(CollectionAccess).where(
                and_(
                    CollectionAccess.collection_id == collection_id,
                    CollectionAccess.user_id == user_id,
                )
            )

            result = await db.execute(query)
            await db.commit()

            return result.rowcount > 0

        except Exception as e:
            await db.rollback()
            logger.error(f"Error revoking collection access: {e}")
            raise

    @staticmethod
    async def get_collection_access(
        db: AsyncSession, collection_id: UUID
    ) -> List[CollectionAccess]:
        """Get all access entries for a collection (alias for get_collection_access_list)"""
        return await CollectionAccessCRUD.get_collection_access_list(db, collection_id)

    @staticmethod
    async def update_access(
        db: AsyncSession, collection_id: UUID, user_id: UUID, updates: CollectionAccessUpdate
    ) -> Optional[CollectionAccess]:
        """Update access permissions for a user"""
        try:
            # Check if access exists
            existing_query = select(CollectionAccess).where(
                and_(
                    CollectionAccess.collection_id == collection_id,
                    CollectionAccess.user_id == user_id,
                )
            )
            existing_result = await db.execute(existing_query)
            existing_access = existing_result.scalar_one_or_none()

            if not existing_access:
                return None

            # Build update dictionary
            update_data = {}
            for field, value in updates.dict(exclude_unset=True).items():
                if value is not None:
                    update_data[field] = value

            if not update_data:
                return existing_access

            # Update access
            update_query = (
                update(CollectionAccess)
                .where(CollectionAccess.id == existing_access.id)
                .values(**update_data)
            )

            await db.execute(update_query)
            await db.commit()

            # Return updated access
            updated_result = await db.execute(existing_query)
            return updated_result.scalar_one()

        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating collection access: {e}")
            raise
