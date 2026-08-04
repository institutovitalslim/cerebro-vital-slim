"""SQLite database construction and schema for hook history."""

from __future__ import annotations

from typing import Any

from sqlalchemy import (
    JSON,
    Column,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    UniqueConstraint,
    create_engine,
    event,
)
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.exc import ArgumentError
from sqlalchemy.pool import StaticPool

metadata = MetaData()

generation_sessions = Table(
    "generation_sessions",
    metadata,
    Column("row_id", Integer, primary_key=True, autoincrement=True),
    Column("session_id", String(36), nullable=False, unique=True),
    Column("created_at", String(40), nullable=False),
)

hooks = Table(
    "hooks",
    metadata,
    Column("row_id", Integer, primary_key=True, autoincrement=True),
    Column(
        "session_id",
        String(36),
        ForeignKey("generation_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("position", Integer, nullable=False),
    Column("hook_id", String(36), nullable=False),
    Column("text", Text, nullable=False),
    Column("language", String(16), nullable=False),
    Column("library", String(32), nullable=False),
    Column("pattern_id", Text, nullable=False),
    Column("mechanisms", JSON, nullable=False),
    Column("objective", String(32), nullable=False),
    Column("channel", String(32), nullable=False),
    Column("awareness_stage", String(32), nullable=False),
    Column("audience", Text, nullable=False),
    Column("topic", Text, nullable=False),
    Column("tone", String(32), nullable=False),
    Column("scores", JSON, nullable=False),
    Column("compliance", JSON, nullable=False),
    Column("explanation", Text, nullable=False),
    Column("source", String(32), nullable=False),
    Column("engine_version", String(32), nullable=False),
    Column("created_at", String(40), nullable=False),
    UniqueConstraint("session_id", "hook_id", name="uq_hooks_session_hook"),
    UniqueConstraint("session_id", "position", name="uq_hooks_session_position"),
)

favorites = Table(
    "favorites",
    metadata,
    Column("hook_id", String(36), primary_key=True),
    Column("created_at", String(40), nullable=False),
)


def create_database(url: str) -> Engine:
    """Create an initialized SQLite 2.x engine with FK enforcement.

    In-memory databases use one process-local connection through ``StaticPool`` so
    their contents survive normal connect/begin boundaries. File databases allow
    SQLAlchemy to choose its SQLite-safe thread settings.
    """
    if not isinstance(url, str) or not url.strip():
        raise TypeError("database URL must be a non-empty SQLite URL string")
    try:
        parsed = make_url(url)
    except ArgumentError as exc:
        raise ValueError(f"invalid SQLite database URL: {url!r}") from exc
    if parsed.get_backend_name() != "sqlite":
        raise ValueError(f"only SQLite URLs are supported, got {parsed.drivername!r}")

    options: dict[str, Any] = {"future": True}
    query = parsed.query
    is_memory = parsed.database in (None, "", ":memory:") or (
        parsed.database is not None
        and parsed.database.startswith("file:")
        and query.get("mode") == "memory"
        and query.get("uri") == "true"
    )
    if is_memory:
        options.update(poolclass=StaticPool, connect_args={"check_same_thread": False})

    engine: Engine | None = None
    try:
        engine = create_engine(url, **options)

        @event.listens_for(engine, "connect")
        def _enable_foreign_keys(dbapi_connection: Any, _connection_record: Any) -> None:
            cursor = dbapi_connection.cursor()
            try:
                cursor.execute("PRAGMA foreign_keys=ON")
            finally:
                cursor.close()

        metadata.create_all(engine)
    except Exception as exc:
        if engine is not None:
            engine.dispose()
        raise RuntimeError(f"failed to initialize SQLite database for URL {url!r}") from exc
    return engine
