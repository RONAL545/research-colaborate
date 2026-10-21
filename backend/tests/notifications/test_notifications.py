import os
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.main import create_app
from app.modules.applications.models import Application
from app.modules.auth.models import User
from app.modules.notifications.models import Notification
from app.modules.notifications.service import create_notification
from app.modules.projects.models import Project
from app.schemas.identity import Principal, Role
from app.schemas.notifications import NotificationKind


@pytest.fixture
def setup():
    url = os.environ["DATABASE_URL"]
    assert "test" in url and url.startswith("postgresql")
    command.upgrade(Config("alembic.ini"), "head")
    engine = create_engine(url)
    ids = [uuid4(), uuid4()]
    with Session(engine) as db:
        db.execute(delete(Notification))
        for uid in ids:
            db.add(
                User(
                    id=uid,
                    email=f"{uid}@unaj.edu.pe",
                    password_hash="unused",
                    name="Student",
                    university="UNAJ",
                    career="Engineering",
                )
            )
        db.flush()
        project = Project(
            author_id=ids[0],
            university="UNAJ",
            title="Test",
            description="Test",
            category="QA",
            required_roles=["QA"],
            status="recruiting",
        )
        db.add(project)
        db.commit()
        engine.test_project_id = project.id
        engine.test_applicant_id = ids[1]
    app = create_app()

    def database():
        with Session(engine) as db:
            yield db

    app.dependency_overrides[get_db] = database
    with TestClient(app) as api:
        yield api, app, engine, ids
    app.dependency_overrides.clear()
    with Session(engine) as db:
        db.execute(delete(Notification))
        db.execute(delete(Application).where(Application.project_id == engine.test_project_id))
        db.execute(delete(Project).where(Project.id == engine.test_project_id))
        db.execute(delete(User).where(User.id.in_(ids)))
        db.commit()
    engine.dispose()


def identity(app, uid):
    app.dependency_overrides[get_current_user] = lambda: Principal(
        id=uid, university="UNAJ", role=Role.student, email_verified=False
    )


def application(engine):
    with Session(engine) as db:
        item = Application(
            project_id=engine.test_project_id,
            applicant_id=engine.test_applicant_id,
            message="Seed",
            status="rejected",
        )
        db.add(item)
        db.commit()
        return item.id


def seed(engine, uid, count=1):
    application_ids = [application(engine) for _ in range(count)]
    with Session(engine) as db:
        result = [
            create_notification(
                db,
                recipient_id=uid,
                application_id=application_id,
                kind=NotificationKind.application_received,
            )
            for application_id in application_ids
        ]
        db.commit()
        return [str(item.id) for item in result]


def test_anonymous_and_no_creation_endpoint(setup):
    api, _, _, _ = setup
    assert api.get("/api/v1/notifications").status_code == 401
    assert api.patch(f"/api/v1/notifications/{uuid4()}/read").status_code == 401
    assert api.post("/api/v1/notifications", json={}).status_code == 405


def test_isolation_mark_read_idempotent_and_forged_ids(setup):
    api, app, engine, ids = setup
    own = seed(engine, ids[0])[0]
    other = seed(engine, ids[1])[0]
    identity(app, ids[0])
    listed = api.get("/api/v1/notifications", params={"recipient_id": str(ids[1])})
    assert [item["id"] for item in listed.json()["items"]] == [own]
    assert (
        api.patch(
            f"/api/v1/notifications/{other}/read", json={"recipient_id": str(ids[1])}
        ).status_code
        == 404
    )
    assert api.patch(f"/api/v1/notifications/{uuid4()}/read").status_code == 404
    read = api.patch(
        f"/api/v1/notifications/{own}/read", json={"recipient_id": str(ids[1]), "read_at": None}
    )
    assert read.status_code == 200
    assert read.json()["read_at"] is not None
    assert api.patch(f"/api/v1/notifications/{own}/read").json() == read.json()
    assert api.get("/api/v1/notifications?unread_only=true").json()["total"] == 0
    assert api.get("/api/v1/notifications").json()["total"] == 1
    identity(app, ids[1])
    assert api.get("/api/v1/notifications?unread_only=true").json()["total"] == 1


def test_pagination_and_validation(setup):
    api, app, engine, ids = setup
    expected = set(seed(engine, ids[0], 5))
    identity(app, ids[0])
    pages = [api.get(f"/api/v1/notifications?page={p}&page_size=2").json() for p in range(1, 4)]
    actual = [item["id"] for page in pages for item in page["items"]]
    assert len(actual) == len(set(actual)) == 5
    assert set(actual) == expected
    assert all(page["total"] == 5 for page in pages)
    assert api.get("/api/v1/notifications?page_size=2").json() == pages[0]
    assert api.get("/api/v1/notifications?page=4&page_size=2").json()["items"] == []
    for query in ["page=0", "page_size=0", "page_size=101", "unread_only=invalid"]:
        assert api.get(f"/api/v1/notifications?{query}").status_code == 422
    assert api.patch("/api/v1/notifications/invalid/read").status_code == 422


def test_service_idempotence_and_external_rollback(setup):
    _, _, engine, ids = setup
    application_id = application(engine)
    with Session(engine) as db:
        first = create_notification(
            db,
            recipient_id=ids[0],
            application_id=application_id,
            kind=NotificationKind.application_received,
        )
        duplicate = create_notification(
            db,
            recipient_id=ids[0],
            application_id=application_id,
            kind=NotificationKind.application_received,
        )
        assert first.id == duplicate.id
        db.rollback()
    with Session(engine) as db:
        assert db.scalar(select(func.count()).select_from(Notification)) == 0
        first = create_notification(
            db,
            recipient_id=ids[0],
            application_id=application_id,
            kind=NotificationKind.application_received,
        )
        first_id = first.id
        db.commit()
    with Session(engine) as db:
        assert (
            create_notification(
                db,
                recipient_id=ids[0],
                application_id=application_id,
                kind=NotificationKind.application_received,
            ).id
            == first_id
        )
        create_notification(
            db,
            recipient_id=ids[0],
            application_id=application_id,
            kind=NotificationKind.application_accepted,
        )
        db.commit()
        assert db.scalar(select(func.count()).select_from(Notification)) == 2


def test_concurrent_creation_preserves_outer_transactions(setup):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    _, _, engine, ids = setup
    application_id = application(engine)
    barrier = Barrier(2)
    side_application_ids = [application(engine), application(engine)]

    def create(worker):
        with Session(engine) as db:
            original_scalar = db.scalar
            initial_query = True

            def synchronized_scalar(*args, **kwargs):
                nonlocal initial_query
                value = original_scalar(*args, **kwargs)
                if initial_query:
                    initial_query = False
                    barrier.wait(timeout=10)
                return value

            db.scalar = synchronized_scalar
            notification = create_notification(
                db,
                recipient_id=ids[0],
                application_id=application_id,
                kind=NotificationKind.application_received,
            )
            result = notification.id
            # Each worker can continue writing after the uniqueness race.
            create_notification(
                db,
                recipient_id=ids[1],
                application_id=side_application_ids[worker],
                kind=NotificationKind.application_received,
            )
            db.commit()
            return result

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(create, range(2)))
    assert results[0] == results[1]
    with Session(engine) as db:
        assert db.scalar(select(func.count()).select_from(Notification)) == 3
