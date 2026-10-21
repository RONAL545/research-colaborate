"""Transactional ports: implementations must flush but never commit the caller's session."""
from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.schemas.applications import ApplicationStatus


@dataclass(frozen=True)
class ApplicationContext:
    id: UUID
    project_id: UUID
    author_id: UUID
    applicant_id: UUID


class CollaborationActions(Protocol):
    def submitted(self, db: Session, application: ApplicationContext) -> None: ...

    def decided(
        self, db: Session, application: ApplicationContext, status: ApplicationStatus
    ) -> None: ...


class UnconfiguredActions:
    def submitted(self, db: Session, application: ApplicationContext) -> None:
        raise HTTPException(503, "Collaboration integrations are not configured")

    def decided(
        self, db: Session, application: ApplicationContext, status: ApplicationStatus
    ) -> None:
        raise HTTPException(503, "Collaboration integrations are not configured")


def get_collaboration_actions() -> CollaborationActions:
    return UnconfiguredActions()
