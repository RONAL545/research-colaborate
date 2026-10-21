import os

from alembic import command
from alembic.config import Config
from app.core.config import get_settings
from sqlalchemy import create_engine, inspect


def test_migrations_roundtrip():
    assert os.environ.get("DATABASE_URL"), "Set DATABASE_URL to a disposable test database"
    assert "test" in get_settings().database_url.rsplit("/", 1)[-1], "Use a test database"
    config = Config("alembic.ini")
    command.upgrade(config, "head")
    engine = create_engine(get_settings().database_url)
    assert "alembic_version" in inspect(engine).get_table_names()
    command.check(config)
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine.dispose()
