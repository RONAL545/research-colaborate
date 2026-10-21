"""Adapters coordinating transactional side effects of team applications."""

from sqlalchemy.orm import Session

from app.core.collaboration import ApplicationContext
from app.modules.chat.service import open_conversation
from app.modules.notifications.service import create_notification
from app.schemas.applications import ApplicationStatus
from app.schemas.notifications import NotificationKind


class TransactionalCollaborationActions:
    def submitted(self, db: Session, application: ApplicationContext) -> None:
        open_conversation(
            db,
            application_id=application.id,
            project_id=application.project_id,
            author_id=application.author_id,
            applicant_id=application.applicant_id,
        )
        create_notification(
            db,
            recipient_id=application.author_id,
            application_id=application.id,
            kind=NotificationKind.application_received,
        )

    def decided(
        self, db: Session, application: ApplicationContext, status: ApplicationStatus
    ) -> None:
        if status not in (ApplicationStatus.accepted, ApplicationStatus.rejected):
            raise ValueError("Only terminal decisions create notifications")
        create_notification(
            db,
            recipient_id=application.applicant_id,
            application_id=application.id,
            kind=NotificationKind(f"application_{status.value}"),
        )
