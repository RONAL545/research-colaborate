from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True)
    password_hash: Mapped[str] = mapped_column(String(512))
    name: Mapped[str] = mapped_column(String(120))
    university: Mapped[str] = mapped_column(String(200))
    career: Mapped[str] = mapped_column(String(200))
    bio: Mapped[str] = mapped_column(default="")
    skills: Mapped[list[str]] = mapped_column(JSONB, default=list)
    role: Mapped[str] = mapped_column(String(20), default="student")
    email_verified: Mapped[bool] = mapped_column(default=False)


class VerificationToken(Base):
    __tablename__ = "verification_tokens"

    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
