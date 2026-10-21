from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        UniqueConstraint("recipient_id", "application_id", "kind", name="uq_notification_event"),
        CheckConstraint(
            "kind IN ('application_received', 'application_accepted', 'application_rejected')",
            name="ck_notification_kind",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    recipient_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    application_id: Mapped[UUID] = mapped_column(
        ForeignKey("applications.id", name="fk_notifications_application"), index=True
    )
    kind: Mapped[str] = mapped_column(String(30))
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
