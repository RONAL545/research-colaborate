"""Real JWT workflow and transactional boundaries across collaboration modules."""

import os
from uuid import UUID

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.collaboration import get_collaboration_actions
from app.core.database import get_db, get_engine
from app.integrations.collaboration import TransactionalCollaborationActions
from app.main import create_app
from app.modules.applications.models import Application
from app.modules.auth.mail import TestMailbox, get_mailer
from app.modules.auth.models import User, VerificationToken
from app.modules.chat.models import Conversation, Message
from app.modules.notifications.models import Notification


@pytest.fixture
def team():
    assert "test" in os.environ["DATABASE_URL"].rsplit("/", 1)[-1]
    command.upgrade(Config("alembic.ini"), "head")
    with get_engine().connect() as connection:
        transaction = connection.begin()
        app = create_app()
        mailbox = TestMailbox()

        def database():
            # A fresh session per request preserves production rollback-on-close behavior.
            with Session(bind=connection, join_transaction_mode="create_savepoint") as session:
                yield session

        app.dependency_overrides[get_db] = database
        app.dependency_overrides[get_mailer] = lambda: mailbox
        with TestClient(app) as client:
            yield client, connection, mailbox
        app.dependency_overrides.clear()
        transaction.rollback()


def account(client, mailbox, email, verified=True):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "secure password 123",
            "name": "Student",
            "university": "UNAJ",
            "career": "Engineering",
        },
    )
    assert response.status_code == 201
    token = mailbox.messages[-1][1]
    if verified:
        assert client.post("/api/v1/auth/verify", json={"token": token}).status_code == 200
    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "secure password 123",
        },
    )
    assert login.status_code == 200
    return response.json(), {"Authorization": "Bearer " + login.json()["access_token"]}, token


def project(client, headers):
    response = client.post(
        "/api/v1/projects",
        headers=headers,
        json={
            "title": "Research team",
            "description": "Build together",
            "category": "AI",
            "required_roles": ["Backend"],
            "status": "recruiting",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_registration_to_decision_and_private_conversation(team):
    client, connection, mailbox = team
    author, owner, _ = account(client, mailbox, "creator@unaj.edu.pe")
    applicant, candidate, verify_token = account(client, mailbox, "candidate@unaj.edu.pe", False)
    stranger, outsider, _ = account(client, mailbox, "outsider@unaj.edu.pe")
    # Even Admin is not a participant and must not gain access to private resources.
    with Session(bind=connection, join_transaction_mode="create_savepoint") as session:
        session.get(User, UUID(stranger["id"])).role = "admin"
        session.commit()
    project_id = project(client, owner)
    endpoint = f"/api/v1/applications/projects/{project_id}"
    assert (
        client.post(endpoint, headers=candidate, json={"message": "I can help"}).status_code == 403
    )
    assert client.post("/api/v1/auth/verify", json={"token": verify_token}).status_code == 200
    response = client.post(endpoint, headers=candidate, json={"message": "I can help"})
    assert response.status_code == 201
    application = response.json()
    application_id = application["id"]
    assert application["status"] == "pending"
    assert application["applicant_id"] == applicant["id"]
    assert client.post(endpoint, headers=candidate, json={"message": "Again"}).status_code == 409
    own_list = client.get("/api/v1/applications", headers=candidate).json()
    assert own_list["items"][0]["id"] == application_id
    incoming = client.get("/api/v1/applications?scope=received", headers=owner).json()
    assert incoming["items"][0]["id"] == application_id
    notice = client.get("/api/v1/notifications?unread_only=true", headers=owner).json()["items"][0]
    assert notice["application_id"] == application_id
    assert notice["kind"] == "application_received"
    assert notice["read_at"] is None
    read_url = f"/api/v1/notifications/{notice['id']}/read"
    assert client.patch(read_url, headers=outsider).status_code == 404
    assert client.patch(read_url, headers=owner).status_code == 200
    assert client.get("/api/v1/notifications?unread_only=true", headers=owner).json()["total"] == 0
    conversations = client.get("/api/v1/conversations", headers=candidate).json()
    room = conversations["items"][0]
    assert room["application_id"] == application_id
    assert room["author_id"] == author["id"]
    assert room["applicant_id"] == applicant["id"]
    assert client.get("/api/v1/conversations", headers=owner).json()["items"] == [room]
    assert client.get("/api/v1/conversations", headers=outsider).json()["items"] == []
    assert client.get("/api/v1/notifications", headers=outsider).json()["items"] == []
    assert client.get(f"/api/v1/applications/{application_id}", headers=outsider).status_code == 404
    messages = f"/api/v1/conversations/{room['id']}/messages"
    assert client.get(messages, headers=outsider).status_code == 404
    assert client.post(messages, headers=outsider, json={"content": "Intrusion"}).status_code == 404
    sent_messages = []
    for headers, content, sender in [
        (candidate, "I can build the backend", applicant),
        (owner, "Let's discuss", author),
    ]:
        sent = client.post(messages, headers=headers, json={"content": content})
        assert sent.status_code == 201
        assert sent.json()["sender_id"] == sender["id"]
        sent_messages.append(sent.json())
    assert client.get(messages, headers=candidate).json()["items"] == sorted(
        sent_messages, key=lambda message: (message["created_at"], message["id"])
    )
    decision = f"/api/v1/applications/{application_id}"
    assert client.patch(decision, headers=candidate, json={"status": "accepted"}).status_code == 403
    accepted = client.patch(decision, headers=owner, json={"status": "accepted"})
    assert accepted.status_code == 200
    assert accepted.json()["status"] == "accepted"
    assert client.patch(decision, headers=owner, json={"status": "rejected"}).status_code == 409
    notices = client.get("/api/v1/notifications", headers=candidate).json()["items"]
    assert len(notices) == 1 and notices[0]["kind"] == "application_accepted"
    assert client.post(endpoint, headers=candidate, json={"message": "Again"}).status_code == 409


def test_rejected_request_can_reapply_and_existing_chat_stays_private(team):
    client, _, mailbox = team
    _, owner, _ = account(client, mailbox, "creator@unaj.edu.pe")
    _, candidate, _ = account(client, mailbox, "candidate@unaj.edu.pe")
    project_id = project(client, owner)
    endpoint = f"/api/v1/applications/projects/{project_id}"
    first = client.post(endpoint, headers=candidate, json={"message": "First"}).json()
    assert (
        client.patch(
            f"/api/v1/applications/{first['id']}", headers=owner, json={"status": "rejected"}
        ).status_code
        == 200
    )
    second = client.post(endpoint, headers=candidate, json={"message": "New proposal"})
    assert second.status_code == 201
    assert second.json()["id"] != first["id"]
    assert client.get("/api/v1/conversations", headers=candidate).json()["total"] == 2
    notices = client.get("/api/v1/notifications", headers=candidate).json()["items"]
    assert notices[0]["kind"] == "application_rejected"
    assert client.get("/api/v1/notifications", headers=owner).json()["total"] == 2


@pytest.mark.parametrize("phase", ["submitted", "decided"])
def test_real_collaboration_side_effects_rollback_together(team, phase):
    client, connection, mailbox = team
    _, owner, _ = account(client, mailbox, "creator@unaj.edu.pe")
    _, candidate, _ = account(client, mailbox, "candidate@unaj.edu.pe")
    project_id = project(client, owner)
    endpoint = f"/api/v1/applications/projects/{project_id}"

    class FailingActions(TransactionalCollaborationActions):
        def submitted(self, db, application):
            super().submitted(db, application)
            if phase == "submitted":
                raise RuntimeError("Failure after creating real chat and notification")

        def decided(self, db, application, status):
            super().decided(db, application, status)
            raise RuntimeError("Failure after creating real decision notification")

    if phase == "submitted":
        client.app.dependency_overrides[get_collaboration_actions] = lambda: FailingActions()
        with pytest.raises(RuntimeError):
            client.post(endpoint, headers=candidate, json={"message": "Rollback"})
        with Session(connection) as db:
            for model in [Application, Conversation, Notification, Message]:
                assert db.scalar(select(func.count()).select_from(model)) == 0
    else:
        application = client.post(endpoint, headers=candidate, json={"message": "Persist"}).json()
        client.app.dependency_overrides[get_collaboration_actions] = lambda: FailingActions()
        with pytest.raises(RuntimeError):
            client.patch(
                f"/api/v1/applications/{application['id']}",
                headers=owner,
                json={"status": "accepted"},
            )
        assert (
            client.get(f"/api/v1/applications/{application['id']}", headers=owner).json()["status"]
            == "pending"
        )
        assert client.get("/api/v1/notifications", headers=candidate).json()["items"] == []
        assert client.get("/api/v1/conversations", headers=candidate).json()["total"] == 1


def test_concurrent_real_requests_create_one_chat_and_one_notification_per_event():
    """Independent HTTP requests and DB connections, without identity or action fakes."""
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    from sqlalchemy import delete

    from app.modules.projects.models import Project

    assert "test" in os.environ["DATABASE_URL"].rsplit("/", 1)[-1]
    command.upgrade(Config("alembic.ini"), "head")
    app = create_app()
    mailbox = TestMailbox()
    app.dependency_overrides[get_mailer] = lambda: mailbox
    emails = ["race-creator@unaj.edu.pe", "race-candidate@unaj.edu.pe"]
    try:
        with TestClient(app) as client:
            author, owner, _ = account(client, mailbox, emails[0])
            applicant, candidate, _ = account(client, mailbox, emails[1])
            project_id = project(client, owner)
        barrier = Barrier(2)

        def submit(_):
            with TestClient(create_app()) as client:
                barrier.wait(timeout=10)
                response = client.post(
                    f"/api/v1/applications/projects/{project_id}",
                    headers=candidate,
                    json={"message": "Concurrent request"},
                )
                return response.status_code, response.json()

        with ThreadPoolExecutor(2) as executor:
            results = list(executor.map(submit, range(2)))
        assert sorted(code for code, _ in results) == [201, 409]
        application = next(item for code, item in results if code == 201)
        application_id = UUID(application["id"])
        barrier = Barrier(2)

        def decide(status):
            with TestClient(create_app()) as client:
                barrier.wait(timeout=10)
                response = client.patch(
                    f"/api/v1/applications/{application_id}", headers=owner, json={"status": status}
                )
                return response.status_code

        with ThreadPoolExecutor(2) as executor:
            assert sorted(executor.map(decide, ["accepted", "rejected"])) == [200, 409]
        with Session(get_engine()) as db:
            saved = db.get(Application, application_id)
            assert saved.status in ("accepted", "rejected")
            rooms = db.scalars(
                select(Conversation).where(Conversation.application_id == application_id)
            ).all()
            notices = db.scalars(
                select(Notification).where(Notification.application_id == application_id)
            ).all()
            assert len(rooms) == 1
            assert {(str(n.recipient_id), n.kind) for n in notices} == {
                (author["id"], "application_received"),
                (applicant["id"], f"application_{saved.status}"),
            }
            assert len(notices) == 2
    finally:
        app.dependency_overrides.clear()
        with Session(get_engine()) as db:
            users = select(User.id).where(User.email.in_(emails))
            projects = select(Project.id).where(Project.author_id.in_(users))
            applications = select(Application.id).where(Application.project_id.in_(projects))
            rooms = select(Conversation.id).where(Conversation.project_id.in_(projects))
            db.execute(delete(Message).where(Message.conversation_id.in_(rooms)))
            db.execute(delete(Notification).where(Notification.application_id.in_(applications)))
            db.execute(delete(Conversation).where(Conversation.project_id.in_(projects)))
            db.execute(delete(Application).where(Application.project_id.in_(projects)))
            db.execute(delete(Project).where(Project.author_id.in_(users)))
            db.execute(delete(VerificationToken).where(VerificationToken.user_id.in_(users)))
            db.execute(delete(User).where(User.email.in_(emails)))
            db.commit()
