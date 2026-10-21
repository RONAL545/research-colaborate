"""Private application notifications."""
import sqlalchemy as sa
from alembic import op

revision = "0008_notifications"
down_revision = "0007_merge_events"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "notifications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("recipient_id", sa.Uuid(), nullable=False),
        sa.Column("application_id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.String(30), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(),
                  nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["recipient_id"], ["users.id"]),
        sa.UniqueConstraint("recipient_id", "application_id", "kind",
                            name="uq_notification_event"),
        sa.CheckConstraint(
            "kind IN ('application_received', 'application_accepted', 'application_rejected')",
            name="ck_notification_kind"),
    )
    op.create_index("ix_notifications_recipient_id", "notifications", ["recipient_id"])
    op.create_index("ix_notifications_application_id", "notifications", ["application_id"])


def downgrade():
    op.drop_table("notifications")
