from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_verified
from app.modules.projects.models import Project
from app.schemas.common import Page
from app.schemas.identity import Principal
from app.schemas.projects import ProjectCreate, ProjectRead, ProjectStatus

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectRead, status_code=201)
def create_project(
    data: ProjectCreate,
    user: Principal = Depends(require_verified),
    db: Session = Depends(get_db),
):
    project = Project(**data.model_dump(), author_id=user.id, university=user.university)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=Page[ProjectRead])
def list_projects(
    q: str | None = None,
    university: str | None = None,
    category: str | None = None,
    status: ProjectStatus | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    filters = []
    if q:
        filters.append(
            or_(
                Project.title.icontains(q, autoescape=True),
                Project.description.icontains(q, autoescape=True),
            )
        )
    for column, value in (
        (Project.university, university),
        (Project.category, category),
        (Project.status, status),
    ):
        if value is not None:
            filters.append(column == value)
    total = db.scalar(select(func.count()).select_from(Project).where(*filters))
    items = db.scalars(
        select(Project)
        .where(*filters)
        .order_by(Project.created_at.desc(), Project.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def find_project(db: Session, project_id: UUID) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(404, "Project not found")
    return project


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: UUID, db: Session = Depends(get_db)):
    return find_project(db, project_id)


@router.put("/{project_id}", response_model=ProjectRead)
def replace_project(
    project_id: UUID,
    data: ProjectCreate,
    user: Principal = Depends(require_verified),
    db: Session = Depends(get_db),
):
    project = find_project(db, project_id)
    if project.author_id != user.id:
        raise HTTPException(403, "Only the author can edit this project")
    for field, value in data.model_dump().items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project
