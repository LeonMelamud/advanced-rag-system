"""fix_chat_sessions_defaults

Revision ID: fix_chat_sessions_004
Revises: fix_chat_sessions_003
Create Date: 2025-06-01 11:20:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "fix_chat_sessions_004"
down_revision = "fix_chat_sessions_003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Make problematic fields nullable or add defaults
    op.alter_column("chat_sessions", "status", nullable=True, schema="chat")

    op.alter_column("chat_sessions", "model_name", nullable=True, schema="chat")

    op.alter_column("chat_sessions", "temperature", nullable=True, schema="chat")

    op.alter_column("chat_sessions", "max_tokens", nullable=True, schema="chat")

    op.alter_column("chat_sessions", "message_count", nullable=True, schema="chat")

    op.alter_column("chat_sessions", "title", nullable=True, schema="chat")


def downgrade() -> None:
    # Revert to not null (this might fail if there are null values)
    op.alter_column("chat_sessions", "title", nullable=False, schema="chat")

    op.alter_column("chat_sessions", "message_count", nullable=False, schema="chat")

    op.alter_column("chat_sessions", "max_tokens", nullable=False, schema="chat")

    op.alter_column("chat_sessions", "temperature", nullable=False, schema="chat")

    op.alter_column("chat_sessions", "model_name", nullable=False, schema="chat")

    op.alter_column("chat_sessions", "status", nullable=False, schema="chat")
