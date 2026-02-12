"""add group chat fields

Revision ID: c3a7b12c9d10
Revises: d55b107b5372
Create Date: 2026-02-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c3a7b12c9d10"
down_revision: Union[str, Sequence[str], None] = "d55b107b5372"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("conversations", sa.Column("name", sa.String(length=120), nullable=True))
    op.add_column("conversations", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("conversations", sa.Column("avatar_url", sa.String(length=255), nullable=True))
    op.add_column("conversations", sa.Column("created_by", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "fk_conversations_created_by_users",
        "conversations",
        "users",
        ["created_by"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column(
        "conversation_members",
        sa.Column("role", sa.String(length=20), server_default="member", nullable=False),
    )
    op.add_column(
        "conversation_members",
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_unique_constraint(
        "uq_conversation_member",
        "conversation_members",
        ["conversation_id", "user_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_conversation_member", "conversation_members", type_="unique")
    op.drop_column("conversation_members", "joined_at")
    op.drop_column("conversation_members", "role")

    op.drop_constraint(
        "fk_conversations_created_by_users",
        "conversations",
        type_="foreignkey",
    )
    op.drop_column("conversations", "created_by")
    op.drop_column("conversations", "avatar_url")
    op.drop_column("conversations", "description")
    op.drop_column("conversations", "name")
