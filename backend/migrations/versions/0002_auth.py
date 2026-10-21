"""Authentication users and hashed single-use verification tokens."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002_auth"
down_revision = "0001_bootstrap"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(512), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("university", sa.String(200), nullable=False),
        sa.Column("career", sa.String(200), nullable=False),
        sa.Column("bio", sa.String(), nullable=False),
        sa.Column("skills", postgresql.JSONB(), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("email_verified", sa.Boolean(), nullable=False),
    )
    op.create_table(
        "verification_tokens",
        sa.Column("token_hash", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_verification_tokens_user_id", "verification_tokens", ["user_id"])


def downgrade():
    op.drop_table("verification_tokens")
    op.drop_table("users")
