from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Index, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (Index("ix_projects_feed", "created_at", "id"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    author_id: Mapped[UUID] = mapped_column(index=True)
    university: Mapped[str] = mapped_column(String(200), index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(100), index=True)
    skills: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    required_roles: Mapped[list[str]] = mapped_column(ARRAY(String))
    status: Mapped[str] = mapped_column(String(20), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
