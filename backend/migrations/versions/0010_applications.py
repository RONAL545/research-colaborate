"""Project applications and active-application uniqueness."""
import sqlalchemy as sa
from alembic import op

revision = "0010_applications"
down_revision = "0007_merge_events"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "applications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("applicant_id", sa.Uuid(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["applicant_id"], ["users.id"]),
        sa.CheckConstraint("status IN ('pending','accepted','rejected')", name="ck_applications_status"),
    )
    op.create_index("ix_applications_project_id", "applications", ["project_id"])
    op.create_index("ix_applications_applicant_id", "applications", ["applicant_id"])
    op.create_index("ix_applications_feed", "applications", ["created_at", "id"])
    op.create_index("uq_applications_active", "applications", ["project_id", "applicant_id"],
                    unique=True, postgresql_where=sa.text("status IN ('pending','accepted')"))


def downgrade():
    op.drop_table("applications")
