"""fix_message_role_enum

Revision ID: fix_message_role_005
Revises: fix_chat_sessions_004
Create Date: 2025-06-01 11:25:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "fix_message_role_005"
down_revision = "fix_chat_sessions_004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the existing enum and recreate with correct values
    op.execute("DROP TYPE IF EXISTS chat.messagerole CASCADE")

    # Create the enum with lowercase values to match the code
    op.execute("CREATE TYPE chat.messagerole AS ENUM ('user', 'assistant', 'system')")

    # Add the role column back with the correct enum type
    op.execute(
        """
        ALTER TABLE chat.chat_messages 
        ADD COLUMN role_new chat.messagerole
    """
    )

    # Update existing data (if any) - convert uppercase to lowercase
    op.execute(
        """
        UPDATE chat.chat_messages 
        SET role_new = CASE 
            WHEN role::text = 'USER' THEN 'user'::chat.messagerole
            WHEN role::text = 'ASSISTANT' THEN 'assistant'::chat.messagerole
            WHEN role::text = 'SYSTEM' THEN 'system'::chat.messagerole
            ELSE 'user'::chat.messagerole
        END
    """
    )

    # Drop the old column and rename the new one
    op.execute("ALTER TABLE chat.chat_messages DROP COLUMN role")
    op.execute("ALTER TABLE chat.chat_messages RENAME COLUMN role_new TO role")

    # Make the column not null
    op.execute("ALTER TABLE chat.chat_messages ALTER COLUMN role SET NOT NULL")


def downgrade() -> None:
    # Reverse the changes - create uppercase enum
    op.execute("DROP TYPE IF EXISTS chat.messagerole CASCADE")
    op.execute("CREATE TYPE chat.messagerole AS ENUM ('USER', 'ASSISTANT', 'SYSTEM')")

    # Add the role column back with the uppercase enum type
    op.execute(
        """
        ALTER TABLE chat.chat_messages 
        ADD COLUMN role_new chat.messagerole
    """
    )

    # Update existing data - convert lowercase to uppercase
    op.execute(
        """
        UPDATE chat.chat_messages 
        SET role_new = CASE 
            WHEN role::text = 'user' THEN 'USER'::chat.messagerole
            WHEN role::text = 'assistant' THEN 'ASSISTANT'::chat.messagerole
            WHEN role::text = 'system' THEN 'SYSTEM'::chat.messagerole
            ELSE 'USER'::chat.messagerole
        END
    """
    )

    # Drop the old column and rename the new one
    op.execute("ALTER TABLE chat.chat_messages DROP COLUMN role")
    op.execute("ALTER TABLE chat.chat_messages RENAME COLUMN role_new TO role")

    # Make the column not null
    op.execute("ALTER TABLE chat.chat_messages ALTER COLUMN role SET NOT NULL")
