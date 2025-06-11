"""
MCP Orchestrator Tools API
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.auth import UserContext, get_current_user
from backend.common.database import get_db

from ..crud.tool import ToolAccessCRUD, ToolCRUD
from ..models.schemas import (
    ToolAccessCreate,
    ToolAccessResponse,
    ToolCreate,
    ToolListResponse,
    ToolResponse,
    ToolStatsResponse,
    ToolUpdate,
)
from ..models.tool import ToolStatus, ToolType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/tools", tags=["tools"])


@router.post("/", response_model=ToolResponse, status_code=status.HTTP_201_CREATED)
async def create_tool(
    tool_data: ToolCreate,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new tool"""
    try:
        tool = await ToolCRUD.create_tool(db=db, owner_id=current_user.user_id, tool_data=tool_data)

        logger.info(f"User {current_user.user_id} created tool {tool.id}")
        return ToolResponse.from_orm(tool)

    except Exception as e:
        logger.error(f"Error creating tool: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create tool"
        )


@router.get("/", response_model=ToolListResponse)
async def list_tools(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: Optional[ToolStatus] = Query(None, alias="status"),
    tool_type: Optional[ToolType] = Query(None),
    search: Optional[str] = Query(None),
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List tools accessible to the current user"""
    try:
        tools = await ToolCRUD.get_user_tools(
            db=db,
            user_id=current_user.user_id,
            limit=limit,
            offset=offset,
            status=status_filter,
            tool_type=tool_type,
            search=search,
        )

        tool_responses = [ToolResponse.from_orm(tool) for tool in tools]

        return ToolListResponse(
            tools=tool_responses, total=len(tool_responses), limit=limit, offset=offset
        )

    except Exception as e:
        logger.error(f"Error listing tools for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve tools"
        )


@router.get("/{tool_id}", response_model=ToolResponse)
async def get_tool(
    tool_id: UUID,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific tool"""
    try:
        tool = await ToolCRUD.get_tool(db=db, tool_id=tool_id, user_id=current_user.user_id)

        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found or access denied"
            )

        return ToolResponse.from_orm(tool)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tool {tool_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve tool"
        )


@router.put("/{tool_id}", response_model=ToolResponse)
async def update_tool(
    tool_id: UUID,
    updates: ToolUpdate,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a tool"""
    try:
        tool = await ToolCRUD.update_tool(
            db=db, tool_id=tool_id, user_id=current_user.user_id, updates=updates
        )

        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found or access denied"
            )

        logger.info(f"User {current_user.user_id} updated tool {tool_id}")
        return ToolResponse.from_orm(tool)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tool {tool_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update tool"
        )


@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool(
    tool_id: UUID,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a tool (owner only)"""
    try:
        success = await ToolCRUD.delete_tool(db=db, tool_id=tool_id, user_id=current_user.user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found or access denied"
            )

        logger.info(f"User {current_user.user_id} deleted tool {tool_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting tool {tool_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete tool"
        )


@router.get("/{tool_id}/stats", response_model=ToolStatsResponse)
async def get_tool_stats(
    tool_id: UUID,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get tool execution statistics"""
    try:
        tool = await ToolCRUD.get_tool(db=db, tool_id=tool_id, user_id=current_user.user_id)

        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found or access denied"
            )

        return ToolStatsResponse(
            tool_id=tool.id,
            execution_count=tool.execution_count,
            success_count=tool.success_count,
            failure_count=tool.failure_count,
            avg_execution_time_ms=tool.avg_execution_time_ms,
            last_executed_at=tool.last_executed_at,
            success_rate=(
                tool.success_count / tool.execution_count if tool.execution_count > 0 else 0.0
            ),
            total_users=0,  # TODO: Implement user count calculation
            active_users_last_30_days=0,  # TODO: Implement active user calculation
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tool stats {tool_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve tool statistics",
        )


@router.get("/{tool_id}/access", response_model=List[ToolAccessResponse])
async def get_tool_access(
    tool_id: UUID,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get tool access permissions (owner only)"""
    try:
        tool = await ToolCRUD.get_tool(db=db, tool_id=tool_id, user_id=current_user.user_id)

        if not tool or tool.owner_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found or access denied"
            )

        access_list = await ToolAccessCRUD.get_tool_access_list(db=db, tool_id=tool_id)

        return [ToolAccessResponse.from_orm(access) for access in access_list]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tool access {tool_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve tool access",
        )


@router.post(
    "/{tool_id}/access", response_model=ToolAccessResponse, status_code=status.HTTP_201_CREATED
)
async def grant_tool_access(
    tool_id: UUID,
    access_data: ToolAccessCreate,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Grant access to a tool (owner only)"""
    try:
        tool = await ToolCRUD.get_tool(db=db, tool_id=tool_id, user_id=current_user.user_id)

        if not tool or tool.owner_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found or access denied"
            )

        access = await ToolAccessCRUD.grant_access(
            db=db, tool_id=tool_id, granted_by=current_user.user_id, access_data=access_data
        )

        logger.info(f"User {current_user.user_id} granted access to tool {tool_id}")
        return ToolAccessResponse.from_orm(access)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error granting tool access: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to grant tool access"
        )


@router.delete("/{tool_id}/access/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_tool_access(
    tool_id: UUID,
    user_id: UUID,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke tool access (owner only)"""
    try:
        tool = await ToolCRUD.get_tool(db=db, tool_id=tool_id, user_id=current_user.user_id)

        if not tool or tool.owner_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found or access denied"
            )

        success = await ToolAccessCRUD.revoke_access(db=db, tool_id=tool_id, user_id=user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Access record not found"
            )

        logger.info(f"User {current_user.user_id} revoked access to tool {tool_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking tool access: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to revoke tool access"
        )
