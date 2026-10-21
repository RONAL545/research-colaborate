"""Projects and feed indexes, independent of authentication tables."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0003_projects"
down_revision = "0001_bootstrap"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "projects",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("author_id", sa.Uuid(), nullable=False),
        sa.Column("university", sa.String(200), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("skills", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("required_roles", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    for field in ("author_id", "university", "category", "status"):
        op.create_index(f"ix_projects_{field}", "projects", [field])
    op.create_index("ix_projects_feed", "projects", ["created_at", "id"])


def downgrade():
    op.drop_table("projects")
