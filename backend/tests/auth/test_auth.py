import hashlib
import os
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import jwt
import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db, get_engine
from app.main import create_app
from app.modules.auth.mail import TestMailbox, get_mailer
from app.modules.auth.models import User, VerificationToken
from app.modules.auth.security import password_hasher


@pytest.fixture(scope="module", autouse=True)
def prepare_database():
    url = os.environ.get("DATABASE_URL", "")
    assert "test" in url.rsplit("/", 1)[-1], "Set DATABASE_URL to a disposable test database"
    assert url.startswith("postgresql"), "Auth integration tests require PostgreSQL"
    command.upgrade(Config("alembic.ini"), "head")


@pytest.fixture
def context():
    # Roll back every request together; never replace production authentication.
    connection = get_engine().connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    app = create_app()
    mailbox = TestMailbox()
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_mailer] = lambda: mailbox
    with TestClient(app) as client:
        yield client, session, mailbox
    app.dependency_overrides.clear()
    session.close()
    transaction.rollback()
    connection.close()


def register(client, **changes):
    data = dict(
        email="student@unaj.edu.pe",
        password="strong password 123",
        name="Student",
        university="UNAJ",
        career="Engineering",
    )
    return client.post("/api/v1/auth/register", json=data | changes)


def login(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "student@unaj.edu.pe", "password": "strong password 123"},
    )
    assert response.status_code == 200
    return {"Authorization": "Bearer " + response.json()["access_token"]}


def test_registration_security(context):
    client, db, mailbox = context
    response = register(client)
    assert response.status_code == 201
    assert response.json()["role"] == "student"
    assert not response.json()["email_verified"]
    assert "password_hash" not in response.text and "token" not in response.text
    assert register(client).status_code == 409
    assert register(client, email="STUDENT@unaj.edu.pe").status_code == 409
    assert register(client, email="other@example.com").status_code == 422
    assert register(client, role="admin").status_code == 422
    assert register(client, email_verified=True).status_code == 422
    user = db.scalar(select(User))
    assert user.password_hash.startswith("$argon2")
    assert password_hasher.verify("strong password 123", user.password_hash)
    token = mailbox.messages[0][1]
    assert db.get(VerificationToken, hashlib.sha256(token.encode()).hexdigest())
    assert not db.get(VerificationToken, token)


def test_verification_expiration_resend_and_reuse(context):
    client, db, mailbox = context
    register(client)
    original = mailbox.messages[-1][1]
    db.scalar(select(VerificationToken)).expires_at = datetime.now(UTC) - timedelta(seconds=1)
    db.commit()
    assert client.post("/api/v1/auth/verify", json={"token": original}).status_code == 400
    known = client.post("/api/v1/auth/resend-verification", json={"email": "student@unaj.edu.pe"})
    unknown = client.post("/api/v1/auth/resend-verification", json={"email": "absent@unaj.edu.pe"})
    assert known.json() == unknown.json()
    second = mailbox.messages[-1][1]
    client.post("/api/v1/auth/resend-verification", json={"email": "student@unaj.edu.pe"})
    newest = mailbox.messages[-1][1]
    assert client.post("/api/v1/auth/verify", json={"token": second}).status_code == 400
    assert client.post("/api/v1/auth/verify", json={"token": newest}).status_code == 200
    assert client.post("/api/v1/auth/verify", json={"token": newest}).status_code == 400
    assert client.post("/api/v1/auth/verify", json={"token": "garbage"}).status_code == 400
    count = len(mailbox.messages)
    assert (
        client.post(
            "/api/v1/auth/resend-verification", json={"email": "student@unaj.edu.pe"}
        ).json()
        == known.json()
    )
    assert len(mailbox.messages) == count
    assert client.get("/api/v1/auth/me", headers=login(client)).json()["email_verified"]


def test_login_and_own_profile(context):
    client, db, _ = context
    register(client)
    other = register(client, email="other@unaj.edu.pe").json()
    for email in ["student@unaj.edu.pe", "absent@unaj.edu.pe"]:
        assert (
            client.post(
                "/api/v1/auth/login", json={"email": email, "password": "wrong"}
            ).status_code
            == 401
        )
    headers = login(client)
    profile = client.get("/api/v1/auth/me", headers=headers)
    assert profile.status_code == 200
    data = dict(
        name="New name", university="New university", career="Science", bio="Bio", skills=["Python"]
    )
    changed = client.put("/api/v1/auth/me", headers=headers, json=data)
    assert changed.status_code == 200
    assert changed.json()["skills"] == ["Python"]
    for field, value in [
        ("role", "admin"),
        ("email_verified", True),
        ("id", other["id"]),
        ("email", other["email"]),
    ]:
        assert (
            client.put("/api/v1/auth/me", headers=headers, json=data | {field: value}).status_code
            == 422
        )
    db.expire_all()
    assert db.get(User, UUID(other["id"])).name == "Student"
    assert client.get("/api/v1/auth/me").status_code == 401


@pytest.mark.parametrize(
    "case",
    [
        "malformed",
        "expired",
        "unknown",
        "wrong_key",
        "wrong_algorithm",
        "missing_exp",
        "missing_sub",
        "bad_sub",
    ],
)
def test_invalid_access_tokens(context, case):
    client, _, _ = context
    settings = get_settings()
    user_id = register(client).json()["id"]
    claims = {
        "sub": str(uuid4()) if case == "unknown" else user_id,
        "exp": datetime.now(UTC) + timedelta(minutes=1),
    }
    secret = settings.jwt_secret.get_secret_value()
    algorithm = "HS256"
    if case == "expired":
        claims["exp"] = datetime.now(UTC) - timedelta(minutes=1)
    elif case == "wrong_key":
        secret = "incorrect-signing-secret-32-characters"
    elif case == "wrong_algorithm":
        algorithm = "HS384"
    elif case == "missing_exp":
        del claims["exp"]
    elif case == "missing_sub":
        del claims["sub"]
    elif case == "bad_sub":
        claims["sub"] = "not-a-uuid"
    token = "bad" if case == "malformed" else jwt.encode(claims, secret, algorithm=algorithm)
    assert (
        client.get("/api/v1/auth/me", headers={"Authorization": "Bearer " + token}).status_code
        == 401
    )


def test_configurable_domains(context):
    client, _, _ = context
    settings = get_settings().model_copy(update={"institutional_domains": ["EXAMPLE.EDU"]})
    client.app.dependency_overrides[get_settings] = lambda: settings
    assert register(client).status_code == 422
    assert register(client, email="student@example.edu").status_code == 201
    assert register(client, email="student@sub.example.edu").status_code == 422
