import os
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, update
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.main import create_app
from app.modules.auth.models import User
from app.modules.projects.models import Project
from app.schemas.identity import Principal

URL = "/api/v1/projects"
DATA = {
    "title": "Robótica IA",
    "description": "Una propuesta académica",
    "category": "AI",
    "skills": ["Python"],
    "required_roles": ["QA"],
    "status": "recruiting",
}


@pytest.fixture
def client():
    url = os.environ.get("DATABASE_URL", "")
    assert "test" in url.rsplit("/", 1)[-1], "Use a disposable PostgreSQL test database"
    assert url.startswith("postgresql")
    command.upgrade(Config("alembic.ini"), "head")
    engine = create_engine(url)
    app = create_app()
    app.state.engine = engine

    def database():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = database
    with Session(engine) as session:
        session.execute(delete(Project))
        session.execute(delete(User).where(User.email.like("%@projects-test.invalid")))
        session.commit()
    try:
        with TestClient(app) as test_client:
            yield test_client, app, engine
    finally:
        app.dependency_overrides.clear()
        with Session(engine) as session:
            session.execute(delete(Project))
            session.execute(delete(User).where(User.email.like("%@projects-test.invalid")))
            session.commit()
        engine.dispose()


def identity(app, verified=True, university="UNAJ", user_id=None):
    user = Principal(id=user_id or uuid4(), university=university, email_verified=verified)
    with Session(app.state.engine) as session:
        if session.get(User, user.id) is None:
            session.add(
                User(
                    id=user.id,
                    email=f"{user.id}@projects-test.invalid",
                    password_hash="unused-test-identity",
                    name="Test",
                    university=university,
                    career="Engineering",
                    email_verified=verified,
                )
            )
            session.commit()
    app.dependency_overrides[get_current_user] = lambda: user
    return user


def test_public_reads_and_write_permissions(client):
    http, app, _ = client
    assert http.get(URL).json()["items"] == []
    assert http.post(URL, json=DATA).status_code == 401
    assert http.put(f"{URL}/{uuid4()}", json=DATA).status_code == 401
    identity(app, verified=False)
    assert http.post(URL, json=DATA).status_code == 403
    assert http.put(f"{URL}/{uuid4()}", json=DATA).status_code == 403
    author = identity(app)
    response = http.post(URL, json=DATA)
    assert response.status_code == 201
    project = response.json()
    assert project == {
        **DATA,
        "id": project["id"],
        "author_id": str(author.id),
        "university": "UNAJ",
    }
    app.dependency_overrides.pop(get_current_user)
    assert http.get(f"{URL}/{project['id']}").json() == project
    assert http.get(URL).json()["items"] == [project]
    identity(app)
    assert http.put(f"{URL}/{project['id']}", json=DATA).status_code == 403
    identity(app, user_id=author.id, university="Changed profile")
    replacement = {
        "title": "Updated",
        "description": "New",
        "category": "Hardware",
        "required_roles": ["Backend"],
    }
    updated = http.put(f"{URL}/{project['id']}", json=replacement)
    assert updated.status_code == 200
    assert updated.json() == {**project, **replacement, "skills": [], "status": "idea"}
    assert http.get(f"{URL}/{uuid4()}").status_code == 404
    assert http.put(f"{URL}/{uuid4()}", json=DATA).status_code == 404


@pytest.mark.parametrize(
    "change",
    [
        {"title": " "},
        {"title": "x" * 201},
        {"description": ""},
        {"category": ""},
        {"required_roles": []},
        {"skills": ["x"] * 31},
        {"status": "invalid"},
        {"author_id": str(uuid4())},
        {"university": "Forged"},
    ],
)
def test_payload_validation(client, change):
    http, app, _ = client
    identity(app)
    project_id = http.post(URL, json=DATA).json()["id"]
    for endpoint in (
        lambda: http.post(URL, json={**DATA, **change}),
        lambda: http.put(f"{URL}/{project_id}", json={**DATA, **change}),
    ):
        assert endpoint().status_code == 422
    assert http.get(f"{URL}/{project_id}").json()["title"] == DATA["title"]


@pytest.mark.parametrize("query", ["page=0", "page_size=0", "page_size=101", "status=unknown"])
def test_query_validation(client, query):
    assert client[0].get(f"{URL}?{query}").status_code == 422


def test_combined_filters_search_and_stable_pages(client):
    http, app, engine = client
    for university, category, status, title, description in [
        ("UNAJ", "AI", "recruiting", "Robótica", "Machine LEARNING"),
        ("UNAJ", "AI", "idea", "Learning", "Other"),
        ("OTHER", "AI", "recruiting", "Learning", "Other"),
        ("UNAJ", "Hardware", "recruiting", "Learning", "Other"),
        ("UNAJ", "AI", "recruiting", "100%_literal", "Other"),
    ]:
        identity(app, university=university)
        assert (
            http.post(
                URL,
                json={
                    **DATA,
                    "category": category,
                    "status": status,
                    "title": title,
                    "description": description,
                },
            ).status_code
            == 201
        )
    app.dependency_overrides.pop(get_current_user)
    result = http.get(
        URL,
        params={"q": "learning", "university": "UNAJ", "category": "AI", "status": "recruiting"},
    ).json()
    assert result["total"] == 1
    assert result["items"][0]["title"] == "Robótica"
    assert http.get(URL, params={"q": "%_"}).json()["total"] == 1
    assert http.get(URL, params={"q": "' OR 1=1 --"}).json()["total"] == 0
    with Session(engine) as session:
        session.execute(
            update(Project).values(created_at=datetime(2026, 1, 1, tzinfo=timezone.utc))
        )
        session.commit()
    all_items = http.get(URL).json()["items"]
    assert [item["id"] for item in all_items] == sorted(
        [item["id"] for item in all_items], reverse=True
    )
    pages = [http.get(URL, params={"page": page, "page_size": 2}).json() for page in range(1, 5)]
    assert all(page["total"] == 5 for page in pages)
    assert [item for page in pages for item in page["items"]] == all_items
    assert pages[-1]["items"] == []
