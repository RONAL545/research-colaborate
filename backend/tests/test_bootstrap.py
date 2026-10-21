import pytest
from app.core.config import Settings
from app.core.dependencies import get_current_user
from app.main import create_app
from app.schemas.projects import ProjectCreate
from fastapi.testclient import TestClient
from pydantic import ValidationError


def test_health_and_openapi():
    with TestClient(create_app()) as client:
        assert client.get("/health").json() == {"status": "ok"}
        assert client.get("/openapi.json").status_code == 200


def test_unconfigured_identity_fails_closed():
    from fastapi import Depends

    app = create_app()

    @app.get("/protected")
    def protected(user=Depends(get_current_user)):
        return user

    with TestClient(app) as client:
        assert client.get("/protected").status_code == 401


def test_production_requires_secret():
    with pytest.raises(ValidationError):
        Settings(environment="production", _env_file=None)


def test_contract_rejects_blank_title_and_unknown_fields():
    with pytest.raises(ValidationError):
        ProjectCreate(title="  ", description="idea", category="AI", required_roles=["QA"])
    with pytest.raises(ValidationError):
        ProjectCreate(
            title="Idea",
            description="idea",
            category="AI",
            required_roles=["QA"],
            author_id="forged",
        )
