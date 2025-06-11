"""
MCP Orchestrator Executions API
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.auth import UserContext, get_current_user
from backend.common.database import get_db

from ..crud.tool import ToolAccessCRUD, ToolCRUD, ToolExecutionCRUD
from ..models.schemas import ToolExecutionListResponse, ToolExecutionRequest, ToolExecutionResponse
from ..models.tool import ExecutionStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/executions", tags=["executions"])


@router.post("/", response_model=ToolExecutionResponse, status_code=status.HTTP_201_CREATED)
async def create_execution(
    execution_request: ToolExecutionRequest,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new tool execution"""
    try:
        # Check if user has execute access to the tool
        tool = await ToolCRUD.get_tool(db, execution_request.tool_id, current_user.user_id)
        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found or access denied"
            )

        # Check execute permissions
        if tool.owner_id != current_user.user_id:
            access = await ToolAccessCRUD.get_user_access(
                db, execution_request.tool_id, current_user.user_id
            )
            if not access or not access.can_execute:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Execute permission denied"
                )

        execution = await ToolExecutionCRUD.create_execution(
            db=db, user_id=current_user.user_id, execution_request=execution_request
        )

        logger.info(
            f"User {current_user.user_id} created execution {execution.id} for tool {execution_request.tool_id}"
        )
        return ToolExecutionResponse.from_orm(execution)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating execution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create execution"
        )


@router.get("/", response_model=ToolExecutionListResponse)
async def list_user_executions(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tool_id: Optional[UUID] = Query(None),
    status_filter: Optional[ExecutionStatus] = Query(None, alias="status"),
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List executions for the current user"""
    try:
        executions = await ToolExecutionCRUD.get_user_executions(
            db=db,
            user_id=current_user.user_id,
            limit=limit,
            offset=offset,
            tool_id=tool_id,
            status=status_filter,
        )

        execution_responses = [
            ToolExecutionResponse.from_orm(execution) for execution in executions
        ]

        return ToolExecutionListResponse(
            executions=execution_responses,
            total=len(execution_responses),
            limit=limit,
            offset=offset,
        )

    except Exception as e:
        logger.error(f"Error listing executions for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve executions",
        )


@router.get("/{execution_id}", response_model=ToolExecutionResponse)
async def get_execution(
    execution_id: UUID,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific execution"""
    try:
        # Get execution and check if user has access
        executions = await ToolExecutionCRUD.get_user_executions(
            db=db, user_id=current_user.user_id, limit=1, offset=0
        )

        execution = next((e for e in executions if e.id == execution_id), None)

        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Execution not found or access denied"
            )

        return ToolExecutionResponse.from_orm(execution)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting execution {execution_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve execution"
        )


@router.get("/tools/{tool_id}", response_model=ToolExecutionListResponse)
async def list_tool_executions(
    tool_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List executions for a specific tool (owner only)"""
    try:
        # Check if user is owner of the tool
        tool = await ToolCRUD.get_tool(db, tool_id, current_user.user_id)
        if not tool or tool.owner_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found or access denied"
            )

        executions = await ToolExecutionCRUD.get_tool_executions(
            db=db, tool_id=tool_id, limit=limit, offset=offset
        )

        execution_responses = [
            ToolExecutionResponse.from_orm(execution) for execution in executions
        ]

        return ToolExecutionListResponse(
            executions=execution_responses,
            total=len(execution_responses),
            limit=limit,
            offset=offset,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing tool executions for {tool_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve tool executions",
        )
