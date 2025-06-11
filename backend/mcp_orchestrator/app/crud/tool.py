"""
MCP Orchestrator CRUD Operations
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_, delete, desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.schemas import (
    ToolAccessCreate,
    ToolAccessUpdate,
    ToolCreate,
    ToolExecutionRequest,
    ToolUpdate,
)
from ..models.tool import ExecutionStatus, Tool, ToolAccess, ToolExecution, ToolStatus, ToolType

logger = logging.getLogger(__name__)


class ToolCRUD:
    """CRUD operations for tools"""

    @staticmethod
    async def create_tool(db: AsyncSession, owner_id: UUID, tool_data: ToolCreate) -> Tool:
        """Create a new tool"""
        try:
            tool = Tool(
                name=tool_data.name,
                description=tool_data.description,
                owner_id=owner_id,
                tool_type=tool_data.tool_type,
                configuration=tool_data.configuration,
                parameters_schema=tool_data.parameters_schema,
                return_schema=tool_data.return_schema,
                implementation=tool_data.implementation,
                tags=tool_data.tags,
                tool_metadata=tool_data.tool_metadata,
                version=tool_data.version,
            )

            db.add(tool)
            await db.commit()
            await db.refresh(tool)

            logger.info(f"Created tool {tool.id} for user {owner_id}")
            return tool

        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating tool: {e}")
            raise

    @staticmethod
    async def get_tool(
        db: AsyncSession, tool_id: UUID, user_id: Optional[UUID] = None
    ) -> Optional[Tool]:
        """Get a tool by ID with optional access check"""
        try:
            query = select(Tool).where(Tool.id == tool_id)

            # If user_id provided, check access
            if user_id:
                # User can access if they own it or have explicit access
                access_query = select(ToolAccess).where(
                    and_(
                        ToolAccess.tool_id == tool_id,
                        ToolAccess.user_id == user_id,
                        ToolAccess.can_view == True,
                    )
                )
                access_result = await db.execute(access_query)
                access = access_result.scalar_one_or_none()

                # Check if user is owner or has access
                tool_query = select(Tool).where(
                    and_(
                        Tool.id == tool_id,
                        or_(Tool.owner_id == user_id, access.id.isnot(None) if access else False),
                    )
                )
                result = await db.execute(tool_query)
            else:
                result = await db.execute(query)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting tool {tool_id}: {e}")
            raise

    @staticmethod
    async def get_user_tools(
        db: AsyncSession,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
        status: Optional[ToolStatus] = None,
        tool_type: Optional[ToolType] = None,
        search: Optional[str] = None,
    ) -> List[Tool]:
        """Get tools accessible to a user"""
        try:
            # Get tools where user is owner or has access
            query = (
                select(Tool)
                .join(
                    ToolAccess,
                    and_(
                        ToolAccess.tool_id == Tool.id,
                        ToolAccess.user_id == user_id,
                        ToolAccess.can_view == True,
                    ),
                    isouter=True,
                )
                .where(or_(Tool.owner_id == user_id, ToolAccess.user_id == user_id))
            )

            # Apply filters
            if status:
                query = query.where(Tool.status == status)

            if tool_type:
                query = query.where(Tool.tool_type == tool_type)

            if search:
                search_pattern = f"%{search}%"
                query = query.where(
                    or_(Tool.name.ilike(search_pattern), Tool.description.ilike(search_pattern))
                )

            query = query.order_by(desc(Tool.updated_at)).limit(limit).offset(offset)

            result = await db.execute(query)
            return result.scalars().unique().all()

        except Exception as e:
            logger.error(f"Error getting user tools for {user_id}: {e}")
            raise

    @staticmethod
    async def update_tool(
        db: AsyncSession, tool_id: UUID, user_id: UUID, updates: ToolUpdate
    ) -> Optional[Tool]:
        """Update a tool"""
        try:
            # Check if user has modify access
            tool = await ToolCRUD.get_tool(db, tool_id, user_id)
            if not tool:
                return None

            # Check modify permissions
            if tool.owner_id != user_id:
                access = await ToolAccessCRUD.get_user_access(db, tool_id, user_id)
                if not access or not access.can_modify:
                    return None

            # Build update dictionary
            update_data = {}

            for field, value in updates.dict(exclude_unset=True).items():
                if value is not None:
                    update_data[field] = value

            if not update_data:
                return tool

            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow()

            # Update tool
            query = update(Tool).where(Tool.id == tool_id).values(**update_data)
            await db.execute(query)
            await db.commit()

            # Return updated tool
            return await ToolCRUD.get_tool(db, tool_id, user_id)

        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating tool {tool_id}: {e}")
            raise

    @staticmethod
    async def delete_tool(db: AsyncSession, tool_id: UUID, user_id: UUID) -> bool:
        """Delete a tool (only owner can delete)"""
        try:
            # Check if user is owner
            tool = await ToolCRUD.get_tool(db, tool_id, user_id)
            if not tool or tool.owner_id != user_id:
                return False

            # Delete tool (cascade will handle related records)
            query = delete(Tool).where(Tool.id == tool_id)
            result = await db.execute(query)
            await db.commit()

            return result.rowcount > 0

        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting tool {tool_id}: {e}")
            raise

    @staticmethod
    async def update_tool_stats(
        db: AsyncSession, tool_id: UUID, execution_time_ms: int, success: bool
    ) -> bool:
        """Update tool execution statistics"""
        try:
            # Get current stats
            tool_query = select(Tool).where(Tool.id == tool_id)
            result = await db.execute(tool_query)
            tool = result.scalar_one_or_none()

            if not tool:
                return False

            # Calculate new averages
            new_execution_count = tool.execution_count + 1
            new_success_count = tool.success_count + (1 if success else 0)
            new_failure_count = tool.failure_count + (0 if success else 1)

            # Calculate new average execution time
            if tool.avg_execution_time_ms is None:
                new_avg_time = execution_time_ms
            else:
                total_time = tool.avg_execution_time_ms * tool.execution_count
                new_avg_time = int((total_time + execution_time_ms) / new_execution_count)

            # Update stats
            update_query = (
                update(Tool)
                .where(Tool.id == tool_id)
                .values(
                    execution_count=new_execution_count,
                    success_count=new_success_count,
                    failure_count=new_failure_count,
                    avg_execution_time_ms=new_avg_time,
                    last_executed_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
            )

            await db.execute(update_query)
            await db.commit()

            return True

        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating tool stats {tool_id}: {e}")
            raise


class ToolExecutionCRUD:
    """CRUD operations for tool executions"""

    @staticmethod
    async def create_execution(
        db: AsyncSession, user_id: UUID, execution_request: ToolExecutionRequest
    ) -> ToolExecution:
        """Create a new tool execution"""
        try:
            execution = ToolExecution(
                tool_id=execution_request.tool_id,
                user_id=user_id,
                session_id=execution_request.session_id,
                input_parameters=execution_request.input_parameters,
                execution_context=execution_request.execution_context,
                execution_metadata=execution_request.execution_metadata,
            )

            db.add(execution)
            await db.commit()
            await db.refresh(execution)

            logger.info(f"Created execution {execution.id} for tool {execution_request.tool_id}")
            return execution

        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating execution: {e}")
            raise

    @staticmethod
    async def update_execution_status(
        db: AsyncSession,
        execution_id: UUID,
        status: ExecutionStatus,
        output_result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        execution_time_ms: Optional[int] = None,
        memory_used_mb: Optional[int] = None,
        cpu_usage_percent: Optional[int] = None,
    ) -> Optional[ToolExecution]:
        """Update execution status and results"""
        try:
            update_data = {
                "status": status,
                "completed_at": (
                    datetime.utcnow()
                    if status
                    in [
                        ExecutionStatus.COMPLETED,
                        ExecutionStatus.FAILED,
                        ExecutionStatus.TIMEOUT,
                        ExecutionStatus.CANCELLED,
                    ]
                    else None
                ),
            }

            if output_result is not None:
                update_data["output_result"] = output_result
            if error_message is not None:
                update_data["error_message"] = error_message
            if execution_time_ms is not None:
                update_data["execution_time_ms"] = execution_time_ms
            if memory_used_mb is not None:
                update_data["memory_used_mb"] = memory_used_mb
            if cpu_usage_percent is not None:
                update_data["cpu_usage_percent"] = cpu_usage_percent

            query = (
                update(ToolExecution).where(ToolExecution.id == execution_id).values(**update_data)
            )
            await db.execute(query)
            await db.commit()

            # Get updated execution
            result_query = select(ToolExecution).where(ToolExecution.id == execution_id)
            result = await db.execute(result_query)
            return result.scalar_one_or_none()

        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating execution {execution_id}: {e}")
            raise

    @staticmethod
    async def get_user_executions(
        db: AsyncSession,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
        tool_id: Optional[UUID] = None,
        status: Optional[ExecutionStatus] = None,
    ) -> List[ToolExecution]:
        """Get executions for a user"""
        try:
            query = select(ToolExecution).where(ToolExecution.user_id == user_id)

            if tool_id:
                query = query.where(ToolExecution.tool_id == tool_id)

            if status:
                query = query.where(ToolExecution.status == status)

            query = query.order_by(desc(ToolExecution.started_at)).limit(limit).offset(offset)

            result = await db.execute(query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error getting user executions for {user_id}: {e}")
            raise

    @staticmethod
    async def get_tool_executions(
        db: AsyncSession, tool_id: UUID, limit: int = 50, offset: int = 0
    ) -> List[ToolExecution]:
        """Get executions for a tool"""
        try:
            query = (
                select(ToolExecution)
                .where(ToolExecution.tool_id == tool_id)
                .order_by(desc(ToolExecution.started_at))
                .limit(limit)
                .offset(offset)
            )

            result = await db.execute(query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error getting tool executions for {tool_id}: {e}")
            raise


class ToolAccessCRUD:
    """CRUD operations for tool access control"""

    @staticmethod
    async def grant_access(
        db: AsyncSession, tool_id: UUID, granted_by: UUID, access_data: ToolAccessCreate
    ) -> ToolAccess:
        """Grant access to a tool"""
        try:
            # Check if access already exists
            existing_query = select(ToolAccess).where(
                and_(ToolAccess.tool_id == tool_id, ToolAccess.user_id == access_data.user_id)
            )
            existing_result = await db.execute(existing_query)
            existing_access = existing_result.scalar_one_or_none()

            if existing_access:
                # Update existing access
                update_query = (
                    update(ToolAccess)
                    .where(ToolAccess.id == existing_access.id)
                    .values(
                        can_execute=access_data.can_execute,
                        can_view=access_data.can_view,
                        can_modify=access_data.can_modify,
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
                access = ToolAccess(
                    tool_id=tool_id,
                    user_id=access_data.user_id,
                    can_execute=access_data.can_execute,
                    can_view=access_data.can_view,
                    can_modify=access_data.can_modify,
                    expires_at=access_data.expires_at,
                    granted_by=granted_by,
                )

                db.add(access)
                await db.commit()
                await db.refresh(access)

                logger.info(f"Granted access to tool {tool_id} for user {access_data.user_id}")
                return access

        except Exception as e:
            await db.rollback()
            logger.error(f"Error granting tool access: {e}")
            raise

    @staticmethod
    async def get_user_access(
        db: AsyncSession, tool_id: UUID, user_id: UUID
    ) -> Optional[ToolAccess]:
        """Get user's access to a tool"""
        try:
            query = select(ToolAccess).where(
                and_(ToolAccess.tool_id == tool_id, ToolAccess.user_id == user_id)
            )

            result = await db.execute(query)
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting user access: {e}")
            raise

    @staticmethod
    async def get_tool_access_list(db: AsyncSession, tool_id: UUID) -> List[ToolAccess]:
        """Get all access entries for a tool"""
        try:
            query = (
                select(ToolAccess)
                .where(ToolAccess.tool_id == tool_id)
                .order_by(ToolAccess.granted_at)
            )

            result = await db.execute(query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error getting tool access list: {e}")
            raise

    @staticmethod
    async def update_access(
        db: AsyncSession, tool_id: UUID, user_id: UUID, updates: ToolAccessUpdate
    ) -> Optional[ToolAccess]:
        """Update access permissions for a user"""
        try:
            # Check if access exists
            existing_query = select(ToolAccess).where(
                and_(ToolAccess.tool_id == tool_id, ToolAccess.user_id == user_id)
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
                update(ToolAccess).where(ToolAccess.id == existing_access.id).values(**update_data)
            )

            await db.execute(update_query)
            await db.commit()

            # Return updated access
            updated_result = await db.execute(existing_query)
            return updated_result.scalar_one()

        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating tool access: {e}")
            raise

    @staticmethod
    async def revoke_access(db: AsyncSession, tool_id: UUID, user_id: UUID) -> bool:
        """Revoke user's access to a tool"""
        try:
            query = delete(ToolAccess).where(
                and_(ToolAccess.tool_id == tool_id, ToolAccess.user_id == user_id)
            )

            result = await db.execute(query)
            await db.commit()

            return result.rowcount > 0

        except Exception as e:
            await db.rollback()
            logger.error(f"Error revoking tool access: {e}")
            raise
