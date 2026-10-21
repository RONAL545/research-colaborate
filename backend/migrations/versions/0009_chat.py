"""Private conversations and messages."""
import sqlalchemy as sa
from alembic import op

revision = "0009_chat"
down_revision = "0007_merge_events"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "conversations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("application_id", sa.Uuid(), nullable=False, unique=True),
        sa.Column("project_id", sa.Uuid(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("author_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("applicant_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(),
                  nullable=False),
        sa.CheckConstraint("author_id <> applicant_id", name="ck_conversations_distinct_participants"),
    )
    op.create_index("ix_conversations_author", "conversations", ["author_id", "created_at", "id"])
    op.create_index("ix_conversations_applicant", "conversations", ["applicant_id", "created_at", "id"])
    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("conversation_id", sa.Uuid(), sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("sender_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(),
                  nullable=False),
        sa.CheckConstraint("length(btrim(content)) BETWEEN 1 AND 5000", name="ck_chat_message_content"),
    )
    op.create_index("ix_chat_messages_history", "chat_messages", ["conversation_id", "created_at", "id"])


def downgrade():
    op.drop_table("chat_messages")
    op.drop_table("conversations")
