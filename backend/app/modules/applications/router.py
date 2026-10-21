from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.collaboration import (
    ApplicationContext,
    CollaborationActions,
    get_collaboration_actions,
)
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_verified
from app.modules.applications.models import Application
from app.modules.projects.models import Project
from app.schemas.applications import ApplicationCreate, ApplicationDecision, ApplicationRead
from app.schemas.common import Page
from app.schemas.identity import Principal

router = APIRouter(prefix="/applications", tags=["applications"])


def lock_project(db: Session, project_id: UUID) -> Project:
    project = db.scalar(select(Project).where(Project.id == project_id).with_for_update())
    if project is None:
        raise HTTPException(404, "Project not found")
    return project


def context(application: Application, project: Project) -> ApplicationContext:
    return ApplicationContext(
        application.id, application.project_id, project.author_id, application.applicant_id
    )


@router.post("/projects/{project_id}", response_model=ApplicationRead, status_code=201)
def submit_application(
    project_id: UUID,
    data: ApplicationCreate,
    user: Principal = Depends(require_verified),
    db: Session = Depends(get_db),
    actions: CollaborationActions = Depends(get_collaboration_actions),
):
    try:
        project = lock_project(db, project_id)
        if project.author_id == user.id:
            raise HTTPException(403, "Cannot apply to your own project")
        if project.status != "recruiting":
            raise HTTPException(409, "Project is not recruiting")
        application = Application(project_id=project_id, applicant_id=user.id, message=data.message)
        db.add(application)
        try:
            db.flush()
        except IntegrityError as error:
            if getattr(error.orig, "diag", None) and (
                error.orig.diag.constraint_name == "uq_applications_active"
            ):
                raise HTTPException(409, "An active application already exists") from error
            raise
        actions.submitted(db, context(application, project))
        db.commit()
        db.refresh(application)
        return application
    except Exception:
        db.rollback()
        raise


@router.get("", response_model=Page[ApplicationRead])
def list_applications(
    scope: Literal["sent", "received"] = "sent",
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: Principal = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    criterion = Application.applicant_id == user.id if scope == "sent" else (
        Application.project_id.in_(select(Project.id).where(Project.author_id == user.id))
    )
    total = db.scalar(select(func.count()).select_from(Application).where(criterion))
    items = db.scalars(
        select(Application).where(criterion)
        .order_by(Application.created_at.desc(), Application.id.desc())
        .offset((page - 1) * page_size).limit(page_size)
    ).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{application_id}", response_model=ApplicationRead)
def read_application(
    application_id: UUID,
    user: Principal = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = db.execute(
        select(Application, Project.author_id).join(Project)
        .where(Application.id == application_id)
    ).first()
    if row is None or user.id not in (row[0].applicant_id, row[1]):
        raise HTTPException(404, "Application not found")
    return row[0]


@router.patch("/{application_id}", response_model=ApplicationRead)
def decide_application(
    application_id: UUID,
    data: ApplicationDecision,
    user: Principal = Depends(require_verified),
    db: Session = Depends(get_db),
    actions: CollaborationActions = Depends(get_collaboration_actions),
):
    if data.status == "pending":
        raise HTTPException(422, "Decision must be accepted or rejected")
    try:
        project_id = db.scalar(select(Application.project_id).where(Application.id == application_id))
        if project_id is None:
            raise HTTPException(404, "Application not found")
        project = lock_project(db, project_id)
        if project.author_id != user.id:
            raise HTTPException(403, "Only the project author can decide")
        application = db.scalar(
            select(Application).where(Application.id == application_id).with_for_update()
        )
        if application.status != "pending":
            raise HTTPException(409, "Application already decided")
        application.status = data.status
        db.flush()
        actions.decided(db, context(application, project), data.status)
        db.commit()
        db.refresh(application)
        return application
    except Exception:
        db.rollback()
        raise
