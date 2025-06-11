"""fix_chat_sessions_targeted

Revision ID: fix_chat_sessions_003
Revises: 2aec80ba72dc
Create Date: 2025-06-01 11:15:00.000000

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "fix_chat_sessions_003"
down_revision = "2aec80ba72dc"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing columns to chat_sessions table
    op.add_column(
        "chat_sessions",
        sa.Column("collection_ids", sa.JSON(), nullable=False, server_default="[]"),
        schema="chat",
    )

    op.add_column(
        "chat_sessions",
        sa.Column("context_settings", sa.JSON(), nullable=False, server_default="{}"),
        schema="chat",
    )

    op.add_column(
        "chat_sessions",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        schema="chat",
    )

    # Add missing columns to chat_messages table
    op.add_column(
        "chat_messages",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        schema="chat",
    )

    op.add_column(
        "chat_messages", sa.Column("tokens_used", sa.Integer(), nullable=True), schema="chat"
    )

    op.add_column(
        "chat_messages", sa.Column("response_time_ms", sa.Integer(), nullable=True), schema="chat"
    )


def downgrade() -> None:
    # Remove added columns
    op.drop_column("chat_messages", "response_time_ms", schema="chat")
    op.drop_column("chat_messages", "tokens_used", schema="chat")
    op.drop_column("chat_messages", "user_id", schema="chat")
    op.drop_column("chat_sessions", "is_active", schema="chat")
    op.drop_column("chat_sessions", "context_settings", schema="chat")
    op.drop_column("chat_sessions", "collection_ids", schema="chat")
