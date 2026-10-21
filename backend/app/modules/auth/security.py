from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from fastapi import HTTPException
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.modules.auth.models import User
from app.schemas.identity import Principal

password_hasher = PasswordHash.recommended()
# Equal-cost verification also when the email does not exist.
DUMMY_HASH = password_hasher.hash("unused-dummy-password")
ALGORITHM = "HS256"


def access_token(user: User, settings: Settings) -> str:
    return jwt.encode(
        {
            "sub": str(user.id),
            "exp": datetime.now(UTC) + timedelta(minutes=settings.access_token_minutes),
        },
        settings.jwt_secret.get_secret_value(),
        algorithm=ALGORITHM,
    )


def authenticate(token: str | None, db: Session, settings: Settings) -> Principal:
    try:
        if not token:
            raise ValueError
        claims = jwt.decode(
            token,
            settings.jwt_secret.get_secret_value(),
            algorithms=[ALGORITHM],
            options={"require": ["sub", "exp"]},
        )
        user = db.get(User, UUID(claims["sub"]))
        if user is None:
            raise ValueError
        return Principal.model_validate(user)
    except (jwt.InvalidTokenError, ValueError, TypeError, AttributeError):
        raise HTTPException(
            401, "Invalid authentication", headers={"WWW-Authenticate": "Bearer"}
        ) from None
