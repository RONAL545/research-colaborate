import os
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.main import create_app
from app.modules.events.models import Event
from app.schemas.identity import Principal, Role


@pytest.fixture(scope="session")
def migrated_database():
    url = os.environ["DATABASE_URL"]
    parsed = make_url(url)
    assert parsed.get_backend_name() == "postgresql", "Use disposable PostgreSQL"
    assert "test" in (parsed.database or ""), "Use a test database"
    command.upgrade(Config("alembic.ini"), "head")
    return url


@pytest.fixture
def client(migrated_database):
    url = migrated_database
    engine = create_engine(url)
    with Session(engine) as db:
        db.execute(delete(Event))
        db.commit()
    app = create_app()

    def database():
        with Session(engine) as db:
            yield db

    app.dependency_overrides[get_db] = database
    with TestClient(app) as test_client:
        yield test_client, app
    app.dependency_overrides.clear()
    with Session(engine) as db:
        db.execute(delete(Event))
        db.commit()
    engine.dispose()


def identity(app, role=Role.admin, verified=True):
    app.dependency_overrides[get_current_user] = lambda: Principal(
        id=uuid4(), university="UNAJ", role=role, email_verified=verified
    )


def payload(**changes):
    return {
        "title": "Congreso", "category": "congreso",
        "deadline": "2027-01-10T12:00:00-05:00",
        "url": "https://unaj.edu.pe/congreso", "university": "UNAJ", **changes,
    }


def test_public_empty_directory(client):
    api, _ = client
    response = api.get("/api/v1/events")
    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0, "page": 1, "page_size": 20}


def test_admin_create_public_detail_and_replace(client):
    api, app = client
    identity(app)
    created = api.post("/api/v1/events", json=payload())
    assert created.status_code == 201
    event = created.json()
    assert event["title"] == payload()["title"]
    assert event["created_at"].endswith(("Z", "+00:00"))
    assert event["deadline"] == "2027-01-10T17:00:00Z"
    changed = api.put(f"/api/v1/events/{event['id']}", json=payload(
        title="Semillero", category="semillero", deadline=None
    ))
    assert changed.status_code == 200
    assert changed.json()["deadline"] is None
    assert changed.json()["created_at"] == event["created_at"]
    app.dependency_overrides.pop(get_current_user)
    assert api.get(f"/api/v1/events/{event['id']}").json() == changed.json()
    assert api.get("/api/v1/events").json()["items"] == [changed.json()]


@pytest.mark.parametrize("role,verified,expected", [
    (None, False, 401), (Role.student, True, 403),
    (Role.teacher, True, 403), (Role.admin, False, 403),
])
def test_write_permissions(client, role, verified, expected):
    api, app = client
    if role is not None:
        identity(app, role, verified)
    assert api.post("/api/v1/events", json=payload()).status_code == expected
    assert api.put(f"/api/v1/events/{uuid4()}", json=payload()).status_code == expected
    assert api.get("/api/v1/events").json()["total"] == 0


@pytest.mark.parametrize("changes", [
    {"url": "invalid"}, {"url": "javascript:alert(1)"},
    {"deadline": "tomorrow"}, {"deadline": "2027-01-10T12:00:00"},
    {"title": "   "}, {"category": "invalid"}, {"university": ""},
    {"id": str(uuid4())},
])
def test_invalid_payload(client, changes):
    api, app = client
    identity(app)
    assert api.post("/api/v1/events", json=payload(**changes)).status_code == 422
    assert api.get("/api/v1/events").json()["total"] == 0


def test_pagination_stable_and_bounded(client):
    api, app = client
    identity(app)
    ids = {api.post("/api/v1/events", json=payload(title=f"Event {i}")).json()["id"]
           for i in range(5)}
    pages = [api.get(f"/api/v1/events?page={page}&page_size=2").json()
             for page in range(1, 4)]
    found = [event["id"] for page in pages for event in page["items"]]
    assert len(found) == len(set(found)) == 5
    assert set(found) == ids
    assert all(page["total"] == 5 for page in pages)
    assert api.get("/api/v1/events?page_size=2").json() == pages[0]
    assert api.get("/api/v1/events?page=4&page_size=2").json()["items"] == []
    for query in ["page=0", "page_size=0", "page_size=101"]:
        assert api.get(f"/api/v1/events?{query}").status_code == 422


def test_missing_and_malformed_id(client):
    api, app = client
    identity(app)
    assert api.get(f"/api/v1/events/{uuid4()}").status_code == 404
    assert api.put(f"/api/v1/events/{uuid4()}", json=payload()).status_code == 404
    assert api.get("/api/v1/events/not-a-uuid").status_code == 422
