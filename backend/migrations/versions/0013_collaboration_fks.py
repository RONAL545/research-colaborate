"""Enforce application references after collaboration modules are integrated."""

from alembic import op

revision = "0013_collaboration_fks"
down_revision = "0012_merge_applications"
branch_labels = None
depends_on = None


def upgrade():
    op.create_foreign_key(
        "fk_notifications_application", "notifications", "applications", ["application_id"], ["id"]
    )
    op.create_foreign_key(
        "fk_conversations_application", "conversations", "applications", ["application_id"], ["id"]
    )


def downgrade():
    op.drop_constraint("fk_conversations_application", "conversations", type_="foreignkey")
    op.drop_constraint("fk_notifications_application", "notifications", type_="foreignkey")
