"""fix_chat_sessions_simple

Revision ID: fix_chat_sessions_002
Revises: 2aec80ba72dc
Create Date: 2025-06-01 11:10:00.000000

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "fix_chat_sessions_002"
down_revision = "2aec80ba72dc"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add collection_ids column to existing chat_sessions table
    op.add_column(
        "chat_sessions",
        sa.Column("collection_ids", sa.JSON(), nullable=False, default=list, server_default="[]"),
        schema="chat",
    )

    # Add context_settings column
    op.add_column(
        "chat_sessions",
        sa.Column("context_settings", sa.JSON(), nullable=False, default=dict, server_default="{}"),
        schema="chat",
    )

    # Add is_active column
    op.add_column(
        "chat_sessions",
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True, server_default="true"),
        schema="chat",
    )

    # Modify chat_messages table to match expected schema
    # Add user_id column
    op.add_column(
        "chat_messages",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        schema="chat",
    )

    # Add message_metadata column (rename from existing if needed)
    op.add_column(
        "chat_messages",
        sa.Column(
            "message_metadata_new", sa.JSON(), nullable=False, default=dict, server_default="{}"
        ),
        schema="chat",
    )

    # Add sources column
    op.add_column(
        "chat_messages",
        sa.Column("sources", sa.JSON(), nullable=False, default=list, server_default="[]"),
        schema="chat",
    )

    # Add tokens_used column (rename from token_count)
    op.add_column(
        "chat_messages", sa.Column("tokens_used", sa.Integer(), nullable=True), schema="chat"
    )

    # Add response_time_ms column (rename from processing_time_ms)
    op.add_column(
        "chat_messages", sa.Column("response_time_ms", sa.Integer(), nullable=True), schema="chat"
    )


def downgrade() -> None:
    # Remove added columns
    op.drop_column("chat_messages", "response_time_ms", schema="chat")
    op.drop_column("chat_messages", "tokens_used", schema="chat")
    op.drop_column("chat_messages", "sources", schema="chat")
    op.drop_column("chat_messages", "message_metadata_new", schema="chat")
    op.drop_column("chat_messages", "user_id", schema="chat")
    op.drop_column("chat_sessions", "is_active", schema="chat")
    op.drop_column("chat_sessions", "context_settings", schema="chat")
    op.drop_column("chat_sessions", "collection_ids", schema="chat")
