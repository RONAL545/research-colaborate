from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.chat.models import Conversation


def open_conversation(
    db: Session, *, application_id: UUID, project_id: UUID, author_id: UUID, applicant_id: UUID
) -> Conversation:
    if author_id == applicant_id:
        raise ValueError("Conversation participants must differ")
    query = select(Conversation).where(Conversation.application_id == application_id)
    conversation = db.scalar(query)
    if conversation is None:
        try:
            with db.begin_nested():
                conversation = Conversation(
                    application_id=application_id, project_id=project_id,
                    author_id=author_id, applicant_id=applicant_id,
                )
                db.add(conversation)
                db.flush()
        except IntegrityError:
            conversation = db.scalar(query)
            if conversation is None:
                raise
    if (conversation.project_id, conversation.author_id, conversation.applicant_id) != (
        project_id, author_id, applicant_id
    ):
        raise ValueError("Existing conversation context differs")
    return conversation
