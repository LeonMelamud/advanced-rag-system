"""
MCP Orchestrator Access API
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.auth import UserContext, get_current_user
from backend.common.database import get_db

from ..crud.tool import ToolAccessCRUD, ToolCRUD
from ..models.schemas import ToolAccessResponse, ToolAccessUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/access", tags=["access"])


@router.get("/my-tools", response_model=List[ToolAccessResponse])
async def get_my_tool_access(
    current_user: UserContext = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get all tool access permissions for the current user"""
    try:
        # This would require a new CRUD method to get all access for a user
        # For now, we'll return an empty list as this is a complex query
        # that would need to be implemented in the CRUD layer

        # TODO: Implement ToolAccessCRUD.get_user_all_access()
        return []

    except Exception as e:
        logger.error(f"Error getting user tool access for {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve tool access",
        )


@router.put("/tools/{tool_id}/users/{user_id}", response_model=ToolAccessResponse)
async def update_tool_access(
    tool_id: UUID,
    user_id: UUID,
    updates: ToolAccessUpdate,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update access permissions for a user on a tool (owner only)"""
    try:
        # Check if user is owner
        tool = await ToolCRUD.get_tool(db, tool_id, current_user.user_id)
        if not tool or tool.owner_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found or access denied"
            )

        access = await ToolAccessCRUD.update_access(
            db=db, tool_id=tool_id, user_id=user_id, updates=updates
        )

        if not access:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Access not found")

        logger.info(
            f"User {current_user.user_id} updated access to tool {tool_id} for user {user_id}"
        )
        return ToolAccessResponse.from_orm(access)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tool access {tool_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update tool access"
        )


@router.get("/tools/{tool_id}/users/{user_id}", response_model=ToolAccessResponse)
async def get_user_tool_access(
    tool_id: UUID,
    user_id: UUID,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get specific user's access to a tool (owner only)"""
    try:
        # Check if user is owner
        tool = await ToolCRUD.get_tool(db, tool_id, current_user.user_id)
        if not tool or tool.owner_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found or access denied"
            )

        access = await ToolAccessCRUD.get_user_access(db=db, tool_id=tool_id, user_id=user_id)

        if not access:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Access not found")

        return ToolAccessResponse.from_orm(access)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user tool access {tool_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve tool access",
        )
