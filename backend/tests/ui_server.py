"""Loopback-only E2E server. Never import this application in production."""

import os

import uvicorn
from alembic import command
from alembic.config import Config
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.core.database import get_engine
from app.main import create_app
from app.modules.auth.mail import TestMailbox, get_mailer
from app.modules.auth.models import User
from app.modules.auth.security import password_hasher


def test_app():
    database = make_url(os.environ["DATABASE_URL"])
    if database.get_backend_name() != "postgresql" or not (database.database or "").endswith(
        "_test"
    ):
        raise RuntimeError("UI server requires a disposable PostgreSQL database ending in _test")
    if os.environ.get("UI_E2E_ENABLED") != "1":
        raise RuntimeError("UI_E2E_ENABLED=1 required; this server is only for browser tests")
    command.upgrade(Config("alembic.ini"), "head")
    with Session(get_engine()) as db:
        if db.scalar(select(User).where(User.email == "ui-admin@unaj.edu.pe")) is None:
            db.add(
                User(
                    email="ui-admin@unaj.edu.pe",
                    password_hash=password_hasher.hash("UI-test-password-123"),
                    name="Admin de pruebas",
                    university="UNAJ",
                    career="Investigación",
                    role="admin",
                    email_verified=True,
                )
            )
            db.commit()
    mailbox = TestMailbox()
    app = create_app()
    app.dependency_overrides[get_mailer] = lambda: mailbox

    @app.get("/__test__/verification")
    def verification(email: str):
        for recipient, token in reversed(mailbox.messages):
            if recipient == email:
                return {"token": token}
        raise HTTPException(404, "Test email not found")

    return app


if __name__ == "__main__":
    uvicorn.run(test_app(), host="127.0.0.1", port=int(os.environ.get("UI_BACKEND_PORT", "18000")))
