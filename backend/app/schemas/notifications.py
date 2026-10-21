from datetime import datetime
from enum import StrEnum
from uuid import UUID

from app.schemas.common import DTO


class NotificationKind(StrEnum):
    application_received = "application_received"
    application_accepted = "application_accepted"
    application_rejected = "application_rejected"


class NotificationRead(DTO):
    id: UUID
    application_id: UUID
    kind: NotificationKind
    read_at: datetime | None
    created_at: datetime
