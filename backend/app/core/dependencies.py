from fastapi import Depends, HTTPException, status

from app.schemas.identity import Principal, Role


def get_current_user() -> Principal:
    # Auth replaces this adapter; all modules must depend on this stable function.
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentication required")


def require_verified(user: Principal = Depends(get_current_user)) -> Principal:
    if not user.email_verified:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Verified email required")
    return user


def require_admin(user: Principal = Depends(require_verified)) -> Principal:
    if user.role != Role.admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin role required")
    return user
