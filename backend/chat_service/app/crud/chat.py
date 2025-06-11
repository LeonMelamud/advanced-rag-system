"""
Chat Service CRUD Operations
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_, delete, desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.chat import (
    ChatContext,
    ChatMessage,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatSession,
    ChatSessionCreate,
    ChatSessionResponse,
)

logger = logging.getLogger(__name__)


class ChatSessionCRUD:
    """CRUD operations for chat sessions"""

    @staticmethod
    async def create_session(
        db: AsyncSession, user_id: UUID, session_data: ChatSessionCreate
    ) -> ChatSession:
        """Create a new chat session"""
        try:
            session = ChatSession(
                user_id=user_id,
                title=session_data.title,
                collection_ids=session_data.collection_ids,
                context_settings=session_data.context_settings,
            )

            db.add(session)
            await db.commit()
            await db.refresh(session)

            logger.info(f"Created chat session {session.id} for user {user_id}")
            return session

        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating chat session: {e}")
            raise

    @staticmethod
    async def get_session(
        db: AsyncSession, session_id: UUID, user_id: UUID
    ) -> Optional[ChatSession]:
        """Get a chat session by ID"""
        try:
            query = (
                select(ChatSession)
                .where(and_(ChatSession.id == session_id, ChatSession.user_id == user_id))
                .options(selectinload(ChatSession.messages))
            )

            result = await db.execute(query)
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting chat session {session_id}: {e}")
            raise

    @staticmethod
    async def get_user_sessions(
        db: AsyncSession, user_id: UUID, limit: int = 50, offset: int = 0, active_only: bool = True
    ) -> List[ChatSession]:
        """Get all sessions for a user"""
        try:
            query = select(ChatSession).where(ChatSession.user_id == user_id)

            if active_only:
                query = query.where(ChatSession.is_active == True)

            query = query.order_by(desc(ChatSession.updated_at)).limit(limit).offset(offset)

            result = await db.execute(query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error getting user sessions for {user_id}: {e}")
            raise

    @staticmethod
    async def update_session(
        db: AsyncSession, session_id: UUID, user_id: UUID, updates: Dict[str, Any]
    ) -> Optional[ChatSession]:
        """Update a chat session"""
        try:
            # Add updated_at timestamp
            updates["updated_at"] = datetime.utcnow()

            query = (
                update(ChatSession)
                .where(and_(ChatSession.id == session_id, ChatSession.user_id == user_id))
                .values(**updates)
                .returning(ChatSession)
            )

            result = await db.execute(query)
            await db.commit()

            return result.scalar_one_or_none()

        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating chat session {session_id}: {e}")
            raise

    @staticmethod
    async def delete_session(db: AsyncSession, session_id: UUID, user_id: UUID) -> bool:
        """Delete a chat session (soft delete by marking inactive)"""
        try:
            query = (
                update(ChatSession)
                .where(and_(ChatSession.id == session_id, ChatSession.user_id == user_id))
                .values(is_active=False, updated_at=datetime.utcnow())
            )

            result = await db.execute(query)
            await db.commit()

            return result.rowcount > 0

        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting chat session {session_id}: {e}")
            raise


class ChatMessageCRUD:
    """CRUD operations for chat messages"""

    @staticmethod
    async def create_message(
        db: AsyncSession, session_id: UUID, user_id: UUID, message_data: ChatMessageCreate
    ) -> ChatMessage:
        """Create a new chat message"""
        try:
            message = ChatMessage(
                session_id=session_id,
                user_id=user_id,
                role=message_data.role,
                content=message_data.content,
                message_metadata=message_data.message_metadata,
                sources=message_data.sources,
                tokens_used=message_data.tokens_used,
                response_time_ms=message_data.response_time_ms,
            )

            db.add(message)
            await db.commit()
            await db.refresh(message)

            # Update session timestamp
            await ChatSessionCRUD.update_session(
                db, session_id, user_id, {"updated_at": datetime.utcnow()}
            )

            logger.info(f"Created chat message {message.id} in session {session_id}")
            return message

        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating chat message: {e}")
            raise

    @staticmethod
    async def get_session_messages(
        db: AsyncSession, session_id: UUID, user_id: UUID, limit: int = 100, offset: int = 0
    ) -> List[ChatMessage]:
        """Get messages for a session"""
        try:
            # Verify user has access to session
            session = await ChatSessionCRUD.get_session(db, session_id, user_id)
            if not session:
                return []

            query = (
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at)
                .limit(limit)
                .offset(offset)
            )

            result = await db.execute(query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error getting session messages for {session_id}: {e}")
            raise

    @staticmethod
    async def get_message(
        db: AsyncSession, message_id: UUID, user_id: UUID
    ) -> Optional[ChatMessage]:
        """Get a specific message"""
        try:
            query = select(ChatMessage).where(
                and_(ChatMessage.id == message_id, ChatMessage.user_id == user_id)
            )

            result = await db.execute(query)
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting chat message {message_id}: {e}")
            raise

    @staticmethod
    async def get_conversation_history(
        db: AsyncSession, session_id: UUID, user_id: UUID, max_messages: int = 20
    ) -> List[ChatMessage]:
        """Get recent conversation history for context"""
        try:
            query = (
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(desc(ChatMessage.created_at))
                .limit(max_messages)
            )

            result = await db.execute(query)
            messages = result.scalars().all()

            # Return in chronological order
            return list(reversed(messages))

        except Exception as e:
            logger.error(f"Error getting conversation history for {session_id}: {e}")
            raise


class ChatContextCRUD:
    """CRUD operations for chat context storage"""

    @staticmethod
    async def store_context(
        db: AsyncSession,
        message_id: UUID,
        query_embedding: Optional[List[float]],
        retrieved_chunks: List[Dict[str, Any]],
        merged_context: str,
        context_metadata: Dict[str, Any],
    ) -> ChatContext:
        """Store RAG context for a message"""
        try:
            context = ChatContext(
                message_id=message_id,
                query_embedding=query_embedding,
                retrieved_chunks=retrieved_chunks,
                merged_context=merged_context,
                context_metadata=context_metadata,
            )

            db.add(context)
            await db.commit()
            await db.refresh(context)

            logger.info(f"Stored context for message {message_id}")
            return context

        except Exception as e:
            await db.rollback()
            logger.error(f"Error storing context for message {message_id}: {e}")
            raise

    @staticmethod
    async def get_context(db: AsyncSession, message_id: UUID) -> Optional[ChatContext]:
        """Get stored context for a message"""
        try:
            query = select(ChatContext).where(ChatContext.message_id == message_id)
            result = await db.execute(query)
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting context for message {message_id}: {e}")
            raise
