from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import AwareDatetime, Field, HttpUrl

from app.schemas.common import DTO


class EventCategory(StrEnum):
    congreso = "congreso"
    semillero = "semillero"
    call_for_papers = "call_for_papers"


class EventCreate(DTO):
    title: str = Field(min_length=1, max_length=200)
    category: EventCategory
    deadline: AwareDatetime | None = None
    url: HttpUrl
    university: str = Field(min_length=1, max_length=200)


class EventRead(EventCreate):
    id: UUID
    created_at: datetime
