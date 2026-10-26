"""Database engine and session dependency."""

from collections.abc import Generator
from functools import lru_cache
from pathlib import Path
from typing import Annotated

from alembic import command
from alembic.config import Config
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, get_settings
from app.db.models import Operation, Project, User  # noqa: F401


@lru_cache
def _engine_for(database_url: str) -> Engine:
    """Create and cache an engine for a configured database URL."""
    if database_url.startswith("sqlite:///"):
        db_path = database_url.removeprefix("sqlite:///")
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        return create_engine(
            database_url,
            connect_args={"check_same_thread": False},
        )
    return create_engine(database_url, pool_pre_ping=True)


def get_session_factory(settings: Settings) -> sessionmaker[Session]:
    """Build a session factory from application settings."""
    return sessionmaker(bind=_engine_for(settings.database_url), autoflush=False)


def get_db(settings: Annotated[Settings, Depends(get_settings)]) -> Generator[Session, None, None]:
    """Yield a database session and always close it."""
    session = get_session_factory(settings)()
    try:
        yield session
    finally:
        session.close()


def initialize_database(settings: Settings | None = None) -> None:
    """Apply the checked-in Alembic migrations for local startup."""
    project_root = Path(__file__).resolve().parents[2]
    configured_settings = settings or get_settings()
    if configured_settings.database_url.startswith("sqlite:///"):
        database_path = configured_settings.database_url.removeprefix("sqlite:///")
        if database_path != ":memory:":
            Path(database_path).parent.mkdir(parents=True, exist_ok=True)
    migration_config = Config(str(project_root / "alembic.ini"))
    migration_config.set_main_option("script_location", str(project_root / "migrations"))
    database_url = configured_settings.database_url.replace("%", "%%")
    migration_config.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(migration_config, "head")
