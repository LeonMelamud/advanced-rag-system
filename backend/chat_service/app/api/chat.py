"""
Chat API Endpoints
Handles real-time chat interactions and message processing
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

# Import shared components
from backend.common.database import get_db
from backend.common.auth import get_current_user, UserContext
from backend.common.exceptions import ValidationError, NotFoundError, AuthenticationError

# Import service components
from ..models.chat import ChatSessionCreate, ChatMessageCreate, ChatMessageResponse
from ..models.rag import RAGRequest, StreamingChunk
from ..crud.chat import ChatSessionCRUD, ChatMessageCRUD, ChatContextCRUD
from ..crud.rag import RAGService

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize RAG service
rag_service = RAGService()


class ChatRequest(BaseModel):
    """Chat message request"""

    message: str = Field(..., min_length=1, max_length=10000)
    session_id: Optional[UUID] = None
    collection_ids: List[UUID] = Field(default_factory=list)
    stream: bool = Field(default=True)
    context_settings: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    """Chat message response"""

    message_id: UUID
    session_id: UUID
    content: str
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """
    Send a chat message and get response

    This endpoint handles:
    - Message validation and preprocessing
    - Session management
    - RAG retrieval and context merging
    - LLM response generation
    - Source attribution
    """
    try:
        logger.info(f"Processing chat message from user {current_user.user_id}")

        # Validate collection access (TODO: implement proper RBAC)
        if request.collection_ids:
            # For now, assume user has access to all collections
            pass

        # Get or create session
        session_id = request.session_id
        if not session_id:
            # Create new session
            session_data = ChatSessionCreate(
                title=f"Chat {request.message[:50]}...",
                collection_ids=request.collection_ids,
                context_settings=request.context_settings,
            )
            session = await ChatSessionCRUD.create_session(db, current_user.user_id, session_data)
            session_id = session.id
        else:
            # Verify session exists and user has access
            session = await ChatSessionCRUD.get_session(db, session_id, current_user.user_id)
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
                )

        # Store user message
        user_message_data = ChatMessageCreate(
            role="user",
            content=request.message,
            metadata={"collection_ids": request.collection_ids},
        )
        user_message = await ChatMessageCRUD.create_message(
            db, session_id, current_user.user_id, user_message_data
        )

        # Process RAG request
        rag_request = RAGRequest(
            query=request.message,
            collection_ids=request.collection_ids or [],
            top_k=5,
            context_settings=request.context_settings,
            user_id=UUID(current_user.user_id),
            session_id=session_id,
        )

        rag_response = await rag_service.process_rag_request(rag_request)

        # Store assistant response
        assistant_message_data = ChatMessageCreate(
            role="assistant",
            content=rag_response.response,
            metadata=rag_response.metadata,
            sources=[source.dict() for source in rag_response.sources],
            tokens_used=rag_response.tokens_used,
            response_time_ms=rag_response.processing_time_ms,
        )
        assistant_message = await ChatMessageCRUD.create_message(
            db, session_id, current_user.user_id, assistant_message_data
        )

        # Store context in background
        background_tasks.add_task(store_rag_context, db, assistant_message.id, rag_response)

        return ChatResponse(
            message_id=assistant_message.id,
            session_id=session_id,
            content=rag_response.response,
            sources=[source.dict() for source in rag_response.sources],
            metadata=rag_response.metadata,
        )

    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except AuthenticationError as e:
        logger.warning(f"Authentication error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process message"
        )


@router.post("/stream")
async def stream_message(
    request: ChatRequest,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Send a chat message and stream the response

    Returns a streaming response with chunks of type:
    - status: Processing status updates
    - content: Partial response content
    - source: Source attribution information
    - metadata: Response metadata
    - error: Error information
    - done: End of stream marker
    """
    try:
        logger.info(f"Starting streaming chat for user {current_user.user_id}")

        # Validate collection access (TODO: implement proper RBAC)
        if request.collection_ids:
            pass

        # Get or create session
        session_id = request.session_id
        if not session_id:
            session_data = ChatSessionCreate(
                title=f"Chat {request.message[:50]}...",
                collection_ids=request.collection_ids,
                context_settings=request.context_settings,
            )
            session = await ChatSessionCRUD.create_session(db, current_user.user_id, session_data)
            session_id = session.id

        # Store user message
        user_message_data = ChatMessageCreate(
            role="user",
            content=request.message,
            metadata={"collection_ids": request.collection_ids},
        )
        user_message = await ChatMessageCRUD.create_message(
            db, session_id, current_user.user_id, user_message_data
        )

        async def generate_stream():
            """Generate streaming response"""
            try:
                # Send session info
                yield f"data: {StreamingChunk(type='session', data={'session_id': str(session_id)}).json()}\n\n"

                # Process RAG request with streaming
                rag_request = RAGRequest(
                    query=request.message,
                    collection_ids=request.collection_ids or [],
                    top_k=5,
                    context_settings=request.context_settings,
                    user_id=UUID(current_user.user_id),
                    session_id=session_id,
                )

                # Collect response content and metadata
                response_content = ""
                sources = []
                metadata = {}

                async for chunk in rag_service.process_streaming_rag_request(rag_request):
                    yield f"data: {chunk.json()}\n\n"

                    # Collect data for storage
                    if chunk.type == "content":
                        response_content += chunk.data
                    elif chunk.type == "source":
                        sources.append(chunk.data)
                    elif chunk.type == "metadata":
                        metadata.update(chunk.data)

                # Store assistant response
                if response_content:
                    assistant_message_data = ChatMessageCreate(
                        role="assistant",
                        content=response_content,
                        metadata=metadata,
                        sources=sources,
                        tokens_used=metadata.get("tokens_used"),
                        response_time_ms=metadata.get("response_time_ms"),
                    )
                    await ChatMessageCRUD.create_message(
                        db, session_id, current_user.user_id, assistant_message_data
                    )

            except Exception as e:
                logger.error(f"Error in streaming: {e}", exc_info=True)
                error_chunk = StreamingChunk(
                    type="error", data={"error": "Streaming failed", "details": str(e)}
                )
                yield f"data: {error_chunk.json()}\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            },
        )

    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except AuthenticationError as e:
        logger.warning(f"Authentication error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    except Exception as e:
        logger.error(f"Error starting streaming chat: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start streaming chat",
        )


@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: UUID,
    current_user: UserContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
    """Get chat history for a session"""
    try:
        # Verify session access
        session = await ChatSessionCRUD.get_session(db, session_id, current_user.user_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

        messages = await ChatMessageCRUD.get_session_messages(
            db, session_id, current_user.user_id, limit, offset
        )

        return {
            "session_id": session_id,
            "messages": [ChatMessageResponse.from_orm(msg) for msg in messages],
            "total": len(messages),
        }

    except Exception as e:
        logger.error(f"Error getting chat history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get chat history"
        )


async def store_rag_context(db: AsyncSession, message_id: UUID, rag_response):
    """Background task to store RAG context"""
    try:
        await ChatContextCRUD.store_context(
            db=db,
            message_id=message_id,
            query_embedding=None,  # Could store embedding if needed
            retrieved_chunks=[chunk.dict() for chunk in rag_response.sources],
            merged_context=rag_response.context_used,
            context_metadata=rag_response.metadata,
        )
        logger.info(f"Stored RAG context for message {message_id}")

    except Exception as e:
        logger.error(f"Error storing RAG context: {e}", exc_info=True)
