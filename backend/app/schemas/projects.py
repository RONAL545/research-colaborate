from enum import StrEnum
from uuid import UUID

from pydantic import Field

from app.schemas.common import DTO


class ProjectStatus(StrEnum):
    idea = "idea"
    recruiting = "recruiting"
    in_progress = "in_progress"


class ProjectCreate(DTO):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=10000)
    category: str = Field(min_length=1, max_length=100)
    skills: list[str] = Field(default_factory=list, max_length=30)
    required_roles: list[str] = Field(min_length=1, max_length=30)
    status: ProjectStatus = ProjectStatus.idea


class ProjectRead(ProjectCreate):
    id: UUID
    author_id: UUID
    university: str
