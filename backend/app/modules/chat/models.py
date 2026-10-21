from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = (
        CheckConstraint("author_id <> applicant_id", name="ck_conversations_distinct_participants"),
        Index("ix_conversations_author", "author_id", "created_at", "id"),
        Index("ix_conversations_applicant", "applicant_id", "created_at", "id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    application_id: Mapped[UUID] = mapped_column(unique=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"))
    author_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    applicant_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Message(Base):
    __tablename__ = "chat_messages"
    __table_args__ = (
        CheckConstraint("length(btrim(content)) BETWEEN 1 AND 5000", name="ck_chat_message_content"),
        Index("ix_chat_messages_history", "conversation_id", "created_at", "id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    conversation_id: Mapped[UUID] = mapped_column(ForeignKey("conversations.id"))
    sender_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
