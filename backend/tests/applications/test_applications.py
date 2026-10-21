import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.collaboration import UnconfiguredActions, get_collaboration_actions
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.main import create_app
from app.modules.applications.models import Application
from app.modules.applications.router import decide_application, submit_application
from app.modules.auth.models import User
from app.modules.projects.models import Project
from app.schemas.applications import ApplicationCreate, ApplicationDecision
from app.schemas.identity import Principal

URL = "/api/v1/applications"


class Actions:
    def __init__(self, fail=False):
        self.fail = fail
        self.calls = []

    def submitted(self, db, application):
        self.calls.append(("submitted", application))
        if self.fail:
            db.get(Project, application.project_id).title = "Rolled-back port effect"
            db.flush()
            raise HTTPException(503, "Injected failure")

    def decided(self, db, application, status):
        self.calls.append((status, application))
        if self.fail:
            db.get(Project, application.project_id).title = "Rolled-back port effect"
            db.flush()
            raise HTTPException(503, "Injected failure")


@pytest.fixture
def env():
    url = os.environ["DATABASE_URL"]
    assert "test" in url.rsplit("/", 1)[-1]
    command.upgrade(Config("alembic.ini"), "head")
    engine = create_engine(url)
    app = create_app()
    actions = Actions()

    def database():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = database
    app.dependency_overrides[get_collaboration_actions] = lambda: actions
    people = [Principal(id=uuid4(), university="UNAJ", email_verified=True) for _ in range(3)]
    with Session(engine) as db:
        for person in people:
            db.add(
                User(
                    id=person.id,
                    email=f"{person.id}@applications-test.invalid",
                    password_hash="unused",
                    name="Test",
                    university="UNAJ",
                    career="QA",
                )
            )
        db.flush()
        project = Project(
            author_id=people[0].id,
            university="UNAJ",
            title="Test",
            description="Test",
            category="QA",
            required_roles=["QA"],
            status="recruiting",
        )
        db.add(project)
        db.commit()
        project_id = project.id
    with TestClient(app) as http:
        yield http, app, engine, people, project_id, actions
    app.dependency_overrides.clear()
    with Session(engine) as db:
        db.execute(delete(Application))
        db.execute(delete(Project).where(Project.id == project_id))
        db.execute(delete(User).where(User.id.in_([p.id for p in people])))
        db.commit()
    engine.dispose()


def as_user(env, index=1, verified=True):
    person = env[3][index].model_copy(update={"email_verified": verified})
    env[1].dependency_overrides[get_current_user] = lambda: person
    return person


def submit(env):
    return env[0].post(f"{URL}/projects/{env[4]}", json={"message": "I can contribute"})


def test_complete_flow_privacy_and_reapplication(env):
    http, _, _, people, _, actions = env
    as_user(env)
    created = submit(env)
    assert created.status_code == 201
    item = created.json()
    endpoint = f"{URL}/{item['id']}"
    assert item["applicant_id"] == str(people[1].id)
    assert item["status"] == "pending"
    assert actions.calls[0][1].author_id == people[0].id
    assert submit(env).status_code == 409
    assert http.get(URL).json()["total"] == 1
    assert http.get(f"{URL}?scope=received").json()["total"] == 0
    assert http.get(endpoint).status_code == 200
    assert http.patch(endpoint, json={"status": "accepted"}).status_code == 403
    as_user(env, 2)
    assert http.get(endpoint).status_code == 404
    assert http.get(URL).json()["total"] == 0
    assert http.patch(endpoint, json={"status": "rejected"}).status_code == 403
    as_user(env, 0)
    assert http.get(f"{URL}?scope=received").json()["items"] == [item]
    assert http.get(endpoint).status_code == 200
    assert http.patch(endpoint, json={"status": "pending"}).status_code == 422
    assert http.patch(endpoint, json={"status": "rejected"}).status_code == 200
    assert http.patch(endpoint, json={"status": "accepted"}).status_code == 409
    as_user(env)
    second = submit(env)
    assert second.status_code == 201
    assert second.json()["id"] != item["id"]
    as_user(env, 0)
    assert (
        http.patch(f"{URL}/{second.json()['id']}", json={"status": "accepted"}).status_code == 200
    )
    as_user(env)
    assert submit(env).status_code == 409


def test_auth_validation_and_missing(env):
    http = env[0]
    assert submit(env).status_code == 401
    assert http.get(URL).status_code == 401
    as_user(env, verified=False)
    assert submit(env).status_code == 403
    assert http.get(URL).status_code == 200
    as_user(env, 0)
    assert submit(env).status_code == 403
    as_user(env)
    assert http.post(f"{URL}/projects/{uuid4()}", json={"message": "Hi"}).status_code == 404
    assert http.get(f"{URL}/{uuid4()}").status_code == 404
    assert http.patch(f"{URL}/{uuid4()}", json={"status": "accepted"}).status_code == 404
    for payload in (
        {"message": ""},
        {"message": " "},
        {"message": "x" * 2001},
        {"message": "Hi", "applicant_id": str(uuid4())},
    ):
        assert http.post(f"{URL}/projects/{env[4]}", json=payload).status_code == 422
    for query in ("scope=all", "page=0", "page_size=101", "page_size=0"):
        assert http.get(f"{URL}?{query}").status_code == 422


@pytest.mark.parametrize("status", ["idea", "in_progress"])
def test_project_not_recruiting(env, status):
    as_user(env)
    with Session(env[2]) as db:
        db.get(Project, env[4]).status = status
        db.commit()
    assert submit(env).status_code == 409


def test_rollback_on_port_failure(env):
    http, _, engine, _, _, actions = env
    as_user(env)
    actions.fail = True
    assert submit(env).status_code == 503
    with Session(engine) as db:
        assert db.scalar(select(func.count()).select_from(Application)) == 0
        assert db.get(Project, env[4]).title == "Test"
    actions.fail = False
    item = submit(env).json()
    actions.fail = True
    as_user(env, 0)
    assert http.patch(f"{URL}/{item['id']}", json={"status": "accepted"}).status_code == 503
    with Session(engine) as db:
        assert db.get(Application, item["id"]).status == "pending"
        assert db.get(Project, env[4]).title == "Test"


def test_unconfigured_port_fails_closed(env):
    as_user(env)
    env[1].dependency_overrides[get_collaboration_actions] = lambda: UnconfiguredActions()
    assert submit(env).status_code == 503
    with Session(env[2]) as db:
        assert db.scalar(select(func.count()).select_from(Application)) == 0


def test_stable_pagination(env):
    http = env[0]
    as_user(env)
    first = submit(env).json()
    as_user(env, 0)
    http.patch(f"{URL}/{first['id']}", json={"status": "rejected"})
    as_user(env)
    assert submit(env).status_code == 201
    with Session(env[2]) as db:
        db.execute(text("UPDATE applications SET created_at = '2026-01-01T00:00:00Z'"))
        db.commit()
    items = http.get(URL).json()["items"]
    assert [i["id"] for i in items] == sorted([i["id"] for i in items], reverse=True)
    pages = [http.get(URL, params={"page": i, "page_size": 1}).json() for i in (1, 2, 3)]
    assert all(p["total"] == 2 for p in pages)
    assert [i for p in pages for i in p["items"]] == items


def test_concurrent_submissions_and_decisions(env):
    _, _, engine, people, project_id, _ = env
    barrier = Barrier(2)

    def create():
        with Session(engine) as db:
            barrier.wait(timeout=5)
            try:
                item = submit_application(
                    project_id, ApplicationCreate(message="Hello"), people[1], db, Actions()
                )
                return 201, item.id
            except HTTPException as error:
                return error.status_code, None

    with ThreadPoolExecutor(2) as executor:
        results = list(executor.map(lambda _: create(), range(2)))
    assert sorted(r[0] for r in results) == [201, 409]
    application_id = next(r[1] for r in results if r[0] == 201)
    barrier = Barrier(2)

    def decide(status):
        with Session(engine) as db:
            barrier.wait(timeout=5)
            try:
                decide_application(
                    application_id, ApplicationDecision(status=status), people[0], db, Actions()
                )
                return 200
            except HTTPException as error:
                return error.status_code

    with ThreadPoolExecutor(2) as executor:
        results = list(executor.map(decide, ("accepted", "rejected")))
    assert sorted(results) == [200, 409]


def test_database_partial_unique_constraint(env):
    as_user(env)
    assert submit(env).status_code == 201
    with Session(env[2]) as db:
        db.add(Application(project_id=env[4], applicant_id=env[3][1].id, message="Duplicate"))
        with pytest.raises(IntegrityError) as error:
            db.flush()
        assert error.value.orig.diag.constraint_name == "uq_applications_active"
        db.rollback()


def test_unverified_cannot_decide_but_can_read(env):
    as_user(env)
    item = submit(env).json()
    as_user(env, 0, verified=False)
    endpoint = f"{URL}/{item['id']}"
    assert env[0].get(endpoint).status_code == 200
    assert env[0].get(f"{URL}?scope=received").json()["total"] == 1
    assert env[0].patch(endpoint, json={"status": "accepted"}).status_code == 403


def test_submission_observes_concurrent_project_update(env):
    from threading import Event

    engine, people, project_id = env[2], env[3], env[4]
    started = Event()
    with Session(engine) as editor:
        project = editor.scalar(select(Project).where(Project.id == project_id).with_for_update())
        project.status = "in_progress"
        editor.flush()

        def create():
            with Session(engine) as db:
                started.set()
                try:
                    submit_application(
                        project_id, ApplicationCreate(message="Hello"), people[1], db, Actions()
                    )
                    return 201
                except HTTPException as error:
                    return error.status_code

        with ThreadPoolExecutor(1) as executor:
            pending = executor.submit(create)
            assert started.wait(timeout=5)
            editor.commit()
            assert pending.result(timeout=5) == 409
    with Session(engine) as db:
        assert db.scalar(select(func.count()).select_from(Application)) == 0
