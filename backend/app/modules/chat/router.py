from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_verified
from app.modules.chat.models import Conversation, Message
from app.schemas.chat import ConversationRead, MessageCreate, MessageRead
from app.schemas.common import Page
from app.schemas.identity import Principal

router = APIRouter(prefix="/conversations", tags=["chat"])


def participant(conversation_id: UUID, user: Principal, db: Session) -> Conversation:
    conversation = db.get(Conversation, conversation_id)
    if conversation is None or user.id not in (conversation.author_id, conversation.applicant_id):
        raise HTTPException(404, "Conversation not found")
    return conversation


@router.get("", response_model=Page[ConversationRead])
def list_conversations(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    user: Principal = Depends(get_current_user), db: Session = Depends(get_db),
):
    condition = or_(Conversation.author_id == user.id, Conversation.applicant_id == user.id)
    total = db.scalar(select(func.count()).select_from(Conversation).where(condition))
    items = db.scalars(select(Conversation).where(condition).order_by(
        Conversation.created_at.desc(), Conversation.id.desc()
    ).offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{conversation_id}/messages", response_model=Page[MessageRead])
def list_messages(
    conversation_id: UUID, page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: Principal = Depends(get_current_user), db: Session = Depends(get_db),
):
    participant(conversation_id, user, db)
    condition = Message.conversation_id == conversation_id
    total = db.scalar(select(func.count()).select_from(Message).where(condition))
    items = db.scalars(select(Message).where(condition).order_by(
        Message.created_at.asc(), Message.id.asc()
    ).offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post("/{conversation_id}/messages", response_model=MessageRead, status_code=201)
def send_message(
    conversation_id: UUID, payload: MessageCreate,
    user: Principal = Depends(require_verified), db: Session = Depends(get_db),
):
    participant(conversation_id, user, db)
    message = Message(conversation_id=conversation_id, sender_id=user.id, content=payload.content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message
