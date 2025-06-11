"""fix_chat_sessions_schema

Revision ID: fix_chat_sessions_001
Revises: 2aec80ba72dc
Create Date: 2025-06-01 11:05:00.000000

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "fix_chat_sessions_001"
down_revision = "2aec80ba72dc"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop dependent tables first
    op.drop_table("mcp_executions", schema="mcp")
    op.drop_table("chat_messages", schema="chat")
    op.drop_table("chat_sessions", schema="chat")

    # Create chat_sessions table with collection_ids (plural) as JSON
    op.create_table(
        "chat_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("collection_ids", sa.JSON(), nullable=False, default=list),
        sa.Column("context_settings", sa.JSON(), nullable=False, default=dict),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        schema="chat",
    )

    # Create chat_messages table with correct schema
    op.create_table(
        "chat_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("message_metadata", sa.JSON(), nullable=False, default=dict),
        sa.Column("sources", sa.JSON(), nullable=False, default=list),
        sa.Column("tokens_used", sa.Integer(), nullable=True),
        sa.Column("response_time_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["chat.chat_sessions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="chat",
    )

    # Create chat_contexts table
    op.create_table(
        "chat_contexts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("message_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("query_embedding", sa.JSON(), nullable=True),
        sa.Column("retrieved_chunks", sa.JSON(), nullable=False, default=list),
        sa.Column("merged_context", sa.Text(), nullable=True),
        sa.Column("context_meta", sa.JSON(), nullable=False, default=dict),
        sa.Column("created_at", sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["message_id"],
            ["chat.chat_messages.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="chat",
    )

    # Recreate mcp_executions table
    op.create_table(
        "mcp_executions",
        sa.Column("tool_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING", "RUNNING", "COMPLETED", "FAILED", "TIMEOUT", name="mcpexecutionstatus"
            ),
            nullable=False,
        ),
        sa.Column("input_data", sa.JSON(), nullable=False),
        sa.Column("output_data", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("execution_time_ms", sa.Integer(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["chat.chat_sessions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tool_id"],
            ["mcp.mcp_tools.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["auth.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="mcp",
    )


def downgrade() -> None:
    # Drop the new tables in reverse order
    op.drop_table("mcp_executions", schema="mcp")
    op.drop_table("chat_contexts", schema="chat")
    op.drop_table("chat_messages", schema="chat")
    op.drop_table("chat_sessions", schema="chat")

    # Recreate the old chat_sessions table (if needed for rollback)
    op.create_table(
        "chat_sessions",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("collection_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "ARCHIVED", "DELETED", name="chatsessionstatus"),
            nullable=False,
        ),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column("temperature", sa.Float(), nullable=False),
        sa.Column("max_tokens", sa.Integer(), nullable=False),
        sa.Column("message_count", sa.Integer(), nullable=False),
        sa.Column("last_message_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("settings", sa.JSON(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["collection_id"],
            ["collections.collections.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["auth.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="chat",
    )

    # Recreate old chat_messages table
    op.create_table(
        "chat_messages",
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "role", sa.Enum("USER", "ASSISTANT", "SYSTEM", name="messagerole"), nullable=False
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
        sa.Column("model_used", sa.String(length=100), nullable=True),
        sa.Column("context_chunks", sa.JSON(), nullable=True),
        sa.Column("sources", sa.JSON(), nullable=True),
        sa.Column("message_metadata", sa.JSON(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["chat.chat_sessions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="chat",
    )

    # Recreate old mcp_executions table
    op.create_table(
        "mcp_executions",
        sa.Column("tool_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING", "RUNNING", "COMPLETED", "FAILED", "TIMEOUT", name="mcpexecutionstatus"
            ),
            nullable=False,
        ),
        sa.Column("input_data", sa.JSON(), nullable=False),
        sa.Column("output_data", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("execution_time_ms", sa.Integer(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["chat.chat_sessions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tool_id"],
            ["mcp.mcp_tools.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["auth.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="mcp",
    )
