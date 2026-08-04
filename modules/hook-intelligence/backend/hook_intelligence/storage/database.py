"""SQLite database construction and schema for hook history."""

from __future__ import annotations

import threading
from typing import Any

from sqlalchemy import (
    JSON,
    Column,
    ForeignKey,
    Index,
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


class _SerializedStaticPool(StaticPool):
    """StaticPool with a pre-checkout gate for its single connection record.

    SQLAlchemy increments a connection fairy's checkout counter before dispatching
    ``checkout``. Without this gate, a waiter can increment that counter and block in
    the event, preventing the owner from producing ``checkin``. The event lock still
    owns the complete public checkout/checkin lifecycle; this gate only prevents that
    internal counter race.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.connection_lock = threading.RLock()

    def connect(self) -> Any:
        self.connection_lock.acquire()
        try:
            return super().connect()
        finally:
            self.connection_lock.release()


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
Index("ix_hooks_hook_id", hooks.c.hook_id)

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
    except ArgumentError:
        raise ValueError("invalid SQLite database URL") from None
    if parsed.get_backend_name() != "sqlite":
        raise ValueError("only SQLite URLs are supported")

    options: dict[str, Any] = {"future": True}
    query = parsed.query
    is_memory = parsed.database in (None, "", ":memory:") or (
        parsed.database is not None
        and parsed.database.startswith("file:")
        and query.get("mode") == "memory"
        and query.get("uri") == "true"
    )
    if is_memory:
        options.update(poolclass=_SerializedStaticPool, connect_args={"check_same_thread": False})

    engine: Engine | None = None
    try:
        engine = create_engine(url, **options)

        if is_memory:
            # StaticPool exposes one DBAPI connection. SQLite transactions on that
            # connection must never overlap, so hold an engine-local reentrant lock
            # for the complete checkout/checkin lifecycle. File pools remain fully
            # concurrent and no process-global engine registry is needed.
            pool = engine.pool
            if not isinstance(pool, _SerializedStaticPool):  # defensive invariant
                raise RuntimeError("unexpected SQLite memory pool")

            @event.listens_for(pool, "checkout")
            def _serialize_checkout(*_args: Any) -> None:
                pool.connection_lock.acquire()

            @event.listens_for(pool, "checkin")
            def _serialize_checkin(*_args: Any) -> None:
                pool.connection_lock.release()

        @event.listens_for(engine, "connect")
        def _enable_foreign_keys(dbapi_connection: Any, _connection_record: Any) -> None:
            cursor = dbapi_connection.cursor()
            try:
                cursor.execute("PRAGMA foreign_keys=ON")
            finally:
                cursor.close()

        metadata.create_all(engine)
    except Exception:  # noqa: BLE001 - all initialization failures share a safe API error
        if engine is not None:
            try:
                engine.dispose()
            except Exception:  # noqa: BLE001, S110 - preserve the sanitized API error
                pass
        raise RuntimeError("failed to initialize SQLite database") from None
    return engine
