import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.auth.mail import Mailer, get_mailer
from app.modules.auth.models import User, VerificationToken
from app.modules.auth.security import DUMMY_HASH, access_token, password_hasher
from app.schemas.identity import (
    Login,
    Principal,
    Profile,
    ProfileUpdate,
    Register,
    ResendVerification,
    Token,
    Verification,
)

router = APIRouter(prefix="/auth", tags=["auth"])
GENERIC_MESSAGE = {"message": "If eligible, a verification email will be sent"}


def issue_verification(db: Session, user: User, settings: Settings) -> str:
    now = datetime.now(UTC)
    db.execute(
        update(VerificationToken)
        .where(VerificationToken.user_id == user.id, VerificationToken.consumed_at.is_(None))
        .values(consumed_at=now)
    )
    token = secrets.token_urlsafe(32)
    db.add(
        VerificationToken(
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
            user_id=user.id,
            expires_at=now + timedelta(minutes=settings.verification_token_minutes),
        )
    )
    return token


@router.post("/register", response_model=Profile, status_code=201)
def register(
    data: Register,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    mailer: Mailer = Depends(get_mailer),
):
    email = str(data.email).lower()
    if email.rsplit("@", 1)[1] not in {d.lower() for d in settings.institutional_domains}:
        raise HTTPException(422, "Institutional domain required")
    user = User(
        **data.model_dump(exclude={"password", "email"}),
        email=email,
        password_hash=password_hasher.hash(data.password),
    )
    db.add(user)
    try:
        db.flush()
        token = issue_verification(db, user, settings)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Email already registered") from None
    mailer.send_verification(email, token)
    return user


@router.post("/login", response_model=Token)
def login(data: Login, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    user = db.scalar(select(User).where(User.email == str(data.email).lower()))
    valid = password_hasher.verify(data.password, user.password_hash if user else DUMMY_HASH)
    if not valid or user is None:
        raise HTTPException(401, "Invalid credentials", headers={"WWW-Authenticate": "Bearer"})
    return Token(access_token=access_token(user, settings))


@router.post("/verify")
def verify(data: Verification, db: Session = Depends(get_db)):
    now = datetime.now(UTC)
    user_id = db.scalar(
        update(VerificationToken)
        .where(
            VerificationToken.token_hash == hashlib.sha256(data.token.encode()).hexdigest(),
            VerificationToken.consumed_at.is_(None),
            VerificationToken.expires_at > now,
        )
        .values(consumed_at=now)
        .returning(VerificationToken.user_id)
    )
    if user_id is None:
        raise HTTPException(400, "Invalid or expired verification token")
    db.execute(update(User).where(User.id == user_id).values(email_verified=True))
    db.commit()
    return {"message": "Email verified"}


@router.post("/resend-verification")
def resend(
    data: ResendVerification,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    mailer: Mailer = Depends(get_mailer),
):
    # Serialize reissues for the same account so only the latest token stays active.
    user = db.scalar(select(User).where(User.email == str(data.email).lower()).with_for_update())
    if user and not user.email_verified:
        token = issue_verification(db, user, settings)
        db.commit()
        mailer.send_verification(user.email, token)
    return GENERIC_MESSAGE


@router.get("/me", response_model=Profile)
def me(principal: Principal = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.get(User, principal.id)


@router.put("/me", response_model=Profile)
def update_me(
    data: ProfileUpdate,
    principal: Principal = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.get(User, principal.id)
    for key, value in data.model_dump().items():
        setattr(user, key, value)
    db.commit()
    return user
