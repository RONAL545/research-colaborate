import os
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db, get_engine
from app.main import create_app
from app.modules.auth.mail import TestMailbox, get_mailer
from app.modules.projects.models import Project


@pytest.fixture
def integrated():
    assert "test" in os.environ["DATABASE_URL"].rsplit("/", 1)[-1]
    command.upgrade(Config("alembic.ini"), "head")
    with get_engine().connect() as connection:
        transaction = connection.begin()
        with Session(bind=connection, join_transaction_mode="create_savepoint") as session:
            app = create_app()
            mailbox = TestMailbox()
            app.dependency_overrides[get_db] = lambda: session
            app.dependency_overrides[get_mailer] = lambda: mailbox
            with TestClient(app) as client:
                yield client, session, mailbox
            app.dependency_overrides.clear()
        transaction.rollback()


def student(client, mailbox, email):
    data = dict(
        email=email,
        password="secure password 123",
        name="Student",
        university="UNAJ",
        career="Engineering",
    )
    registered = client.post("/api/v1/auth/register", json=data)
    assert registered.status_code == 201
    login = client.post("/api/v1/auth/login", json={"email": email, "password": data["password"]})
    assert login.status_code == 200
    return (
        registered.json(),
        {"Authorization": "Bearer " + login.json()["access_token"]},
        mailbox.messages[-1][1],
    )


def test_real_identity_verification_project_ownership(integrated):
    client, _, mailbox = integrated
    author, headers, token = student(client, mailbox, "author@unaj.edu.pe")
    data = dict(
        title="Robotics",
        description="Research",
        category="AI",
        required_roles=["Backend"],
        status="recruiting",
    )
    assert client.post("/api/v1/projects", json=data).status_code == 401
    assert client.post("/api/v1/projects", headers=headers, json=data).status_code == 403
    assert client.post("/api/v1/auth/verify", json={"token": token}).status_code == 200
    created = client.post("/api/v1/projects", headers=headers, json=data)
    assert created.status_code == 201
    project = created.json()
    assert project["author_id"] == author["id"]
    assert project["university"] == "UNAJ"
    _, other_headers, other_token = student(client, mailbox, "other@unaj.edu.pe")
    assert client.post("/api/v1/auth/verify", json={"token": other_token}).status_code == 200
    endpoint = f"/api/v1/projects/{project['id']}"
    assert client.put(endpoint, headers=other_headers, json=data).status_code == 403
    assert (
        client.put(endpoint, headers=headers, json=data | {"title": "Updated"}).status_code == 200
    )
    assert (
        client.get("/api/v1/projects", params={"q": "Updated", "university": "UNAJ"}).json()[
            "total"
        ]
        == 1
    )


def test_database_rejects_project_without_existing_author(integrated):
    _, session, _ = integrated
    with pytest.raises(IntegrityError), session.begin_nested():
        session.add(
            Project(
                author_id=uuid4(),
                university="UNAJ",
                title="Orphan",
                description="No author",
                category="AI",
                required_roles=["QA"],
                status="idea",
            )
        )
        session.flush()


def test_real_admin_verification_events_and_role_revocation(integrated):
    from uuid import UUID

    from app.modules.auth.models import User

    client, session, mailbox = integrated
    account, headers, token = student(client, mailbox, "admin@unaj.edu.pe")
    data = dict(
        title="Congress",
        category="congreso",
        deadline="2027-01-10T12:00:00Z",
        url="https://unaj.edu.pe/congreso",
        university="UNAJ",
    )
    assert client.post("/api/v1/events", json=data).status_code == 401
    assert client.post("/api/v1/events", headers=headers, json=data).status_code == 403
    user = session.get(User, UUID(account["id"]))
    user.role = "admin"  # Trusted seed operation, never exposed as an API privilege change.
    session.commit()
    assert client.post("/api/v1/events", headers=headers, json=data).status_code == 403
    assert client.post("/api/v1/auth/verify", json={"token": token}).status_code == 200
    created = client.post("/api/v1/events", headers=headers, json=data)
    assert created.status_code == 201
    endpoint = f"/api/v1/events/{created.json()['id']}"
    updated = client.put(endpoint, headers=headers, json=data | {"title": "Updated Congress"})
    assert updated.status_code == 200
    assert client.get(endpoint).json()["title"] == "Updated Congress"
    assert client.get("/api/v1/events").json()["total"] == 1
    user.role = "student"
    session.commit()
    assert client.put(endpoint, headers=headers, json=data).status_code == 403
    assert client.post("/api/v1/events", headers=headers, json=data).status_code == 403
