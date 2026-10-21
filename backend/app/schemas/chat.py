from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.schemas.common import DTO


class ConversationRead(DTO):
    id: UUID
    application_id: UUID
    project_id: UUID
    author_id: UUID
    applicant_id: UUID
    created_at: datetime


class MessageCreate(DTO):
    content: str = Field(min_length=1, max_length=5000)


class MessageRead(DTO):
    id: UUID
    conversation_id: UUID
    sender_id: UUID
    content: str
    created_at: datetime
