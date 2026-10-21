from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.database import get_db
from app.modules.auth.security import authenticate
from app.schemas.identity import Principal, Role


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Principal:
    return authenticate(credentials.credentials if credentials else None, db, settings)


def require_verified(user: Principal = Depends(get_current_user)) -> Principal:
    if not user.email_verified:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Verified email required")
    return user


def require_admin(user: Principal = Depends(require_verified)) -> Principal:
    if user.role != Role.admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin role required")
    return user
