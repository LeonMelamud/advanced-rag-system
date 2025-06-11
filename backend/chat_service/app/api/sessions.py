"""
Chat Session Management API Endpoints
Handles chat session lifecycle and management
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.auth import UserContext, get_current_user

# Import shared components
from backend.common.database import get_db

from ..crud.chat import ChatMessageCRUD, ChatSessionCRUD

# Import service components
from ..models.chat import ChatSessionCreate, ChatSessionResponse


# Define custom exceptions
class AuthenticationError(Exception):
    """Authentication error"""

    pass


logger = logging.getLogger(__name__)

router = APIRouter()


class CreateSessionRequest(BaseModel):
    """Create session request"""

    title: Optional[str] = Field(None, max_length=255)
    collection_ids: List[UUID] = Field(default_factory=list)
    context_settings: Optional[Dict[str, Any]] = Field(default_factory=dict)


class UpdateSessionRequest(BaseModel):
    """Update session request"""

    title: Optional[str] = Field(None, max_length=255)
    collection_ids: Optional[List[UUID]] = None
    context_settings: Optional[Dict[str, Any]] = None


class SessionResponse(BaseModel):
    """Session response model"""

    id: UUID
    title: Optional[str]
    user_id: UUID
    collection_ids: List[UUID]
    context_settings: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = None


class SessionListResponse(BaseModel):
    """Session list response"""

    sessions: List[SessionResponse]
    total_count: int
    has_more: bool


@router.post("/", response_model=SessionResponse)
async def create_session(
    request: CreateSessionRequest,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new chat session

    Creates a new chat session for the authenticated user with optional
    title, collection associations, and context settings.
    """
    try:
        logger.info(f"Creating new chat session for user {current_user.user_id}")

        # Validate collection access (TODO: implement proper RBAC)
        if request.collection_ids:
            pass

        # Generate title if not provided
        title = request.title or f"Chat Session {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"

        # Create session data
        session_data = ChatSessionCreate(
            title=title,
            collection_ids=request.collection_ids,
            context_settings=request.context_settings or {},
        )

        # Create session in database
        session = await ChatSessionCRUD.create_session(db, current_user.user_id, session_data)

        # Convert to response model
        response = SessionResponse(
            id=session.id,
            title=session.title,
            user_id=session.user_id,
            collection_ids=session.collection_ids,
            context_settings=session.context_settings,
            is_active=session.is_active,
            created_at=session.created_at,
            updated_at=session.updated_at,
            message_count=0,
        )

        logger.info(f"Created chat session {session.id}")
        return response

    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except AuthenticationError as e:
        logger.warning(f"Authentication error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    except Exception as e:
        logger.error(f"Error creating session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create session"
        )


@router.get("/", response_model=SessionListResponse)
async def list_sessions(
    limit: int = 20,
    offset: int = 0,
    search: Optional[str] = None,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List chat sessions for the authenticated user

    Returns a paginated list of chat sessions with optional search filtering.
    """
    try:
        logger.info(f"Listing sessions for user {current_user.user_id}")

        # Get sessions from database
        sessions = await ChatSessionCRUD.get_user_sessions(
            db, current_user.user_id, limit, offset, active_only=True
        )

        # Convert to response models
        session_responses = []
        for session in sessions:
            # Get message count for each session
            messages = await ChatMessageCRUD.get_session_messages(
                db, session.id, current_user.user_id, limit=1
            )

            response = SessionResponse(
                id=session.id,
                title=session.title,
                user_id=session.user_id,
                collection_ids=session.collection_ids,
                context_settings=session.context_settings,
                is_active=session.is_active,
                created_at=session.created_at,
                updated_at=session.updated_at,
                message_count=len(session.messages) if hasattr(session, "messages") else 0,
            )
            session_responses.append(response)

        # Check if there are more sessions
        has_more = len(sessions) == limit

        response = SessionListResponse(
            sessions=session_responses, total_count=len(session_responses), has_more=has_more
        )

        return response

    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except AuthenticationError as e:
        logger.warning(f"Authentication error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    except Exception as e:
        logger.error(f"Error listing sessions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list sessions"
        )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific chat session

    Returns detailed information about a specific chat session.
    """
    try:
        logger.info(f"Retrieving session {session_id} for user {current_user.user_id}")

        # Get session from database
        session = await ChatSessionCRUD.get_session(db, session_id, current_user.user_id)

        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

        # Get message count
        messages = await ChatMessageCRUD.get_session_messages(
            db, session_id, current_user.user_id, limit=1000  # Get all for count
        )

        response = SessionResponse(
            id=session.id,
            title=session.title,
            user_id=session.user_id,
            collection_ids=session.collection_ids,
            context_settings=session.context_settings,
            is_active=session.is_active,
            created_at=session.created_at,
            updated_at=session.updated_at,
            message_count=len(messages),
        )

        return response

    except HTTPException:
        raise

    except AuthenticationError as e:
        logger.warning(f"Authentication error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    except Exception as e:
        logger.error(f"Error retrieving session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve session"
        )


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: UUID,
    request: UpdateSessionRequest,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a chat session

    Updates session title, collection associations, or context settings.
    """
    try:
        logger.info(f"Updating session {session_id} for user {current_user.user_id}")

        # Verify session exists and user has access
        session = await ChatSessionCRUD.get_session(db, session_id, current_user.user_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

        # Build updates dictionary
        updates = {}
        if request.title is not None:
            updates["title"] = request.title
        if request.collection_ids is not None:
            updates["collection_ids"] = request.collection_ids
        if request.context_settings is not None:
            updates["context_settings"] = request.context_settings

        # Update session
        updated_session = await ChatSessionCRUD.update_session(
            db, session_id, current_user.user_id, updates
        )

        if not updated_session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

        # Get message count
        messages = await ChatMessageCRUD.get_session_messages(
            db, session_id, current_user.user_id, limit=1000
        )

        response = SessionResponse(
            id=updated_session.id,
            title=updated_session.title,
            user_id=updated_session.user_id,
            collection_ids=updated_session.collection_ids,
            context_settings=updated_session.context_settings,
            is_active=updated_session.is_active,
            created_at=updated_session.created_at,
            updated_at=updated_session.updated_at,
            message_count=len(messages),
        )

        logger.info(f"Updated session {session_id}")
        return response

    except HTTPException:
        raise

    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except AuthenticationError as e:
        logger.warning(f"Authentication error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    except Exception as e:
        logger.error(f"Error updating session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update session"
        )


@router.delete("/{session_id}")
async def delete_session(
    session_id: UUID,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a chat session

    Soft deletes a chat session by marking it as inactive.
    """
    try:
        logger.info(f"Deleting session {session_id} for user {current_user.user_id}")

        # Delete session (soft delete)
        success = await ChatSessionCRUD.delete_session(db, session_id, current_user.user_id)

        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

        logger.info(f"Deleted session {session_id}")
        return {"message": "Session deleted successfully"}

    except HTTPException:
        raise

    except AuthenticationError as e:
        logger.warning(f"Authentication error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    except Exception as e:
        logger.error(f"Error deleting session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete session"
        )
