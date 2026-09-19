"""SQLAlchemy engine/session composition; models and migrations remain independent of FastAPI."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from backend.app.core.config import Settings


def create_database_engine(settings: Settings) -> Engine:
    """Create a bounded synchronous PostgreSQL engine without logging credentials."""
    database_url = settings.database_url_value
    if not database_url:
        raise RuntimeError("Database is not configured.")
    return create_engine(
        database_url,
        pool_pre_ping=True,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_timeout=settings.database_connect_timeout_seconds,
        connect_args={"connect_timeout": settings.database_connect_timeout_seconds},
    )


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Return non-autocommit sessions; callers own transaction boundaries through the port."""
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_database_session(session_factory: sessionmaker[Session]) -> Generator[Session, None, None]:
    """Yield one request-scoped session and always close it after use."""
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


def database_is_ready(engine: Engine) -> bool:
    """Run a minimal authenticated probe; callers must not disclose failure details."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:  # Database drivers expose several operational exception types.
        return False
    return True
