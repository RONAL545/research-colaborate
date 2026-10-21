from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.notifications.models import Notification
from app.schemas.notifications import NotificationKind


def create_notification(
    db: Session, *, recipient_id: UUID, application_id: UUID, kind: NotificationKind
) -> Notification:
    query = select(Notification).where(
        Notification.recipient_id == recipient_id,
        Notification.application_id == application_id,
        Notification.kind == kind.value,
    )
    existing = db.scalar(query)
    if existing is not None:
        return existing
    try:
        with db.begin_nested():
            notification = Notification(
                recipient_id=recipient_id, application_id=application_id, kind=kind.value
            )
            db.add(notification)
            db.flush()
        return notification
    except IntegrityError:
        existing = db.scalar(query)
        if existing is None:
            raise
        return existing
