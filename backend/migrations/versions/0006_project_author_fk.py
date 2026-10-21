"""Enforce project authors after authentication and projects are integrated."""

from alembic import op

revision = "0006_project_author_fk"
down_revision = "0005_merge_auth_projects"
branch_labels = None
depends_on = None


def upgrade():
    op.create_foreign_key("fk_projects_author_id_users", "projects", "users", ["author_id"], ["id"])


def downgrade():
    op.drop_constraint("fk_projects_author_id_users", "projects", type_="foreignkey")
