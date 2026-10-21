import os
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, select, update
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.main import create_app
from app.modules.auth.models import User
from app.modules.chat.models import Conversation, Message
from app.modules.chat.service import open_conversation
from app.modules.projects.models import Project
from app.schemas.identity import Principal, Role

URL = "/api/v1/conversations"


@pytest.fixture
def setup():
    url = os.environ["DATABASE_URL"]
    assert "test" in url.rsplit("/", 1)[-1]
    command.upgrade(Config("alembic.ini"), "head")
    engine = create_engine(url)
    ids = [uuid4() for _ in range(3)]
    project_id = uuid4()
    with Session(engine) as db:
        db.add_all([User(id=id, email=f"{id}@chat.test", name="Test", university="U",
                         career="C", password_hash="unused", email_verified=True) for id in ids])
        db.flush()
        db.add(Project(id=project_id, author_id=ids[0], university="U", title="T",
                       description="D", category="C", required_roles=["QA"], status="recruiting"))
        db.flush()
        conversation = open_conversation(db, application_id=uuid4(), project_id=project_id,
                                         author_id=ids[0], applicant_id=ids[1])
        cid = conversation.id
        db.commit()
    app = create_app()

    def database():
        with Session(engine) as db:
            yield db

    app.dependency_overrides[get_db] = database
    with TestClient(app) as client:
        yield client, app, engine, ids, cid, project_id
    app.dependency_overrides.clear()
    with Session(engine) as db:
        db.execute(delete(Message))
        db.execute(delete(Conversation))
        db.execute(delete(Project).where(Project.id == project_id))
        db.execute(delete(User).where(User.id.in_(ids)))
        db.commit()
    engine.dispose()


def identity(app, id, verified=True, role=Role.student):
    app.dependency_overrides[get_current_user] = lambda: Principal(
        id=id, university="U", email_verified=verified, role=role
    )


def test_privacy_and_identity(setup):
    http, app, _, ids, cid, _ = setup
    endpoint = f"{URL}/{cid}/messages"
    assert http.get(URL).status_code == 401
    assert http.get(endpoint).status_code == 401
    assert http.post(endpoint, json={"content": "Hello"}).status_code == 401
    for role in (Role.student, Role.admin):
        identity(app, ids[2], role=role)
        assert http.get(URL).json()["total"] == 0
        assert http.get(endpoint).status_code == 404
        assert http.post(endpoint, json={"content": "Hello"}).status_code == 404
    identity(app, ids[0], verified=False)
    assert http.get(endpoint).status_code == 200
    assert http.post(endpoint, json={"content": "Hello"}).status_code == 403
    identity(app, ids[0])
    assert http.post(endpoint, json={"content": "Hello", "sender_id": str(ids[1])}).status_code == 422
    response = http.post(endpoint, json={"content": " Hello "})
    assert response.status_code == 201
    assert response.json()["sender_id"] == str(ids[0])
    assert response.json()["content"] == "Hello"
    identity(app, ids[1])
    assert http.get(endpoint).json()["items"] == [response.json()]
    assert http.get(f"{URL}/{uuid4()}/messages").status_code == 404
    assert http.post(URL, json={}).status_code == 405


@pytest.mark.parametrize("content", ["", " ", "x" * 5001])
def test_message_validation(setup, content):
    http, app, _, ids, cid, _ = setup
    identity(app, ids[0])
    assert http.post(f"{URL}/{cid}/messages", json={"content": content}).status_code == 422


def test_pagination_and_ties(setup):
    http, app, engine, ids, cid, project_id = setup
    identity(app, ids[0])
    endpoint = f"{URL}/{cid}/messages"
    for text in ["a", "b", "x" * 5000]:
        assert http.post(endpoint, json={"content": text}).status_code == 201
    with Session(engine) as db:
        db.execute(update(Message).values(created_at=datetime(2026, 1, 1, tzinfo=timezone.utc)))
        for _ in range(2):
            open_conversation(db, application_id=uuid4(), project_id=project_id,
                              author_id=ids[0], applicant_id=ids[1])
        db.execute(update(Conversation).values(created_at=datetime(2026, 1, 1, tzinfo=timezone.utc)))
        db.commit()
    for path, reverse in [(endpoint, False), (URL, True)]:
        items = http.get(path).json()["items"]
        assert [x["id"] for x in items] == sorted([x["id"] for x in items], reverse=reverse)
        pages = [http.get(path, params={"page": p, "page_size": 1}).json() for p in range(1, 5)]
        assert [x for page in pages for x in page["items"]] == items
        for query in ["page=0", "page_size=0", "page_size=101"]:
            assert http.get(f"{path}?{query}").status_code == 422


def test_idempotence_context_and_external_rollback(setup):
    _, _, engine, ids, _, project_id = setup
    application_id = uuid4()
    args = dict(application_id=application_id, project_id=project_id,
                author_id=ids[0], applicant_id=ids[1])
    with Session(engine) as db:
        first = open_conversation(db, **args)
        assert open_conversation(db, **args).id == first.id
        with pytest.raises(ValueError):
            open_conversation(db, **{**args, "applicant_id": ids[2]})
        with pytest.raises(ValueError):
            open_conversation(db, **{**args, "applicant_id": ids[0]})
        db.rollback()
    with Session(engine) as db:
        assert db.scalar(select(Conversation).where(Conversation.application_id == application_id)) is None


def test_concurrent_open_uses_savepoint(setup):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    from sqlalchemy import event, func

    _, _, engine, ids, _, project_id = setup
    application_id = uuid4()
    barrier = Barrier(2)

    def before_insert(mapper, connection, target):
        if target.application_id == application_id:
            barrier.wait(timeout=10)

    event.listen(Conversation, "before_insert", before_insert)

    def create():
        with Session(engine) as db:
            conversation = open_conversation(
                db, application_id=application_id, project_id=project_id,
                author_id=ids[0], applicant_id=ids[1],
            )
            result = conversation.id
            # A duplicate insert must leave the outer transaction usable.
            assert db.scalar(select(func.count()).select_from(User)) >= 3
            db.commit()
            return result

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(create) for _ in range(2)]
            results = [future.result(timeout=20) for future in futures]
        assert results[0] == results[1]
    finally:
        event.remove(Conversation, "before_insert", before_insert)
