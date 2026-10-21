from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import Field

from app.schemas.common import DTO


class ApplicationStatus(StrEnum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class ApplicationCreate(DTO):
    message: str = Field(min_length=1, max_length=2000)


class ApplicationDecision(DTO):
    status: ApplicationStatus


class ApplicationRead(DTO):
    id: UUID
    project_id: UUID
    applicant_id: UUID
    message: str
    status: ApplicationStatus
    created_at: datetime
    updated_at: datetime
