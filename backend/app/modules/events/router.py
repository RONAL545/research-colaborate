from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.modules.events.models import Event
from app.schemas.common import Page
from app.schemas.events import EventCreate, EventRead
from app.schemas.identity import Principal

router = APIRouter(prefix="/events", tags=["events"])


def find_event(event_id: UUID, db: Session) -> Event:
    event = db.get(Event, event_id)
    if event is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")
    return event


def values(payload: EventCreate) -> dict:
    return {**payload.model_dump(), "url": str(payload.url), "category": payload.category.value}


@router.get("", response_model=Page[EventRead])
def list_events(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    total = db.scalar(select(func.count()).select_from(Event))
    items = db.scalars(
        select(Event).order_by(Event.created_at.desc(), Event.id.desc())
        .offset((page - 1) * page_size).limit(page_size)
    ).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{event_id}", response_model=EventRead)
def get_event(event_id: UUID, db: Session = Depends(get_db)):
    return find_event(event_id, db)


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_event(
    payload: EventCreate,
    admin: Principal = Depends(require_admin),
    db: Session = Depends(get_db),
):
    event = Event(**values(payload))
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.put("/{event_id}", response_model=EventRead)
def replace_event(
    event_id: UUID,
    payload: EventCreate,
    admin: Principal = Depends(require_admin),
    db: Session = Depends(get_db),
):
    event = find_event(event_id, db)
    for name, value in values(payload).items():
        setattr(event, name, value)
    db.commit()
    db.refresh(event)
    return event
