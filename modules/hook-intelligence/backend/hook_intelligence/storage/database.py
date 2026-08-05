"""SQLite database construction and schema for hook history."""

from __future__ import annotations

import sqlite3
import threading
from pathlib import Path
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
    inspect,
    text,
)
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.exc import ArgumentError
from sqlalchemy.pool import StaticPool

metadata = MetaData()
_STANDALONE_ID = "standalone"


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
        self.connection_owner: int | None = None

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
    Column("tenant_id", String(128), nullable=False, server_default=_STANDALONE_ID),
    Column("user_id", String(128), nullable=False, server_default=_STANDALONE_ID),
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
    Column("tenant_id", String(128), nullable=False, server_default=_STANDALONE_ID),
    Column("user_id", String(128), nullable=False, server_default=_STANDALONE_ID),
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
hooks_owner_index = Index(
    "ix_hooks_owner_hook_id", hooks.c.tenant_id, hooks.c.user_id, hooks.c.hook_id
)

favorites = Table(
    "favorites",
    metadata,
    Column("tenant_id", String(128), primary_key=True, server_default=_STANDALONE_ID),
    Column("user_id", String(128), primary_key=True, server_default=_STANDALONE_ID),
    Column("hook_id", String(36), primary_key=True),
    Column("created_at", String(40), nullable=False),
)


def _backup_legacy_file(database_path: str | None) -> None:
    """Create one consistent pre-migration backup for safe code rollback."""

    if not database_path or database_path == ":memory:" or database_path.startswith("file:"):
        return
    source_path = Path(database_path)
    if not source_path.is_file():
        return

    with sqlite3.connect(source_path) as source:
        tables = {
            row[0]
            for row in source.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        if "generation_sessions" not in tables:
            return
        columns = {
            row[1] for row in source.execute("PRAGMA table_info(generation_sessions)").fetchall()
        }
        if {"tenant_id", "user_id"} <= columns:
            return

        backup_path = Path(f"{source_path}.pre-multitenant.bak")
        if backup_path.exists():
            return
        with sqlite3.connect(backup_path) as destination:
            source.backup(destination)


def _migrate_legacy_schema(engine: Engine) -> None:
    """Place pre-ownership rows in the isolated local standalone scope."""

    schema = inspect(engine)
    with engine.begin() as connection:
        for table_name in ("generation_sessions", "hooks"):
            columns = {column["name"] for column in schema.get_columns(table_name)}
            for column_name in ("tenant_id", "user_id"):
                if column_name not in columns:
                    connection.execute(
                        text(
                            f"ALTER TABLE {table_name} ADD COLUMN {column_name} "
                            "VARCHAR(128) NOT NULL DEFAULT 'standalone'"
                        )
                    )

        hooks_owner_index.create(bind=connection, checkfirst=True)

        favorite_columns = {column["name"] for column in schema.get_columns("favorites")}
        favorite_pk = set(schema.get_pk_constraint("favorites").get("constrained_columns") or ())
        expected_columns = {"tenant_id", "user_id", "hook_id", "created_at"}
        expected_pk = {"tenant_id", "user_id", "hook_id"}
        if favorite_columns != expected_columns or favorite_pk != expected_pk:
            connection.execute(
                text(
                    "CREATE TABLE favorites_migrated ("
                    "tenant_id VARCHAR(128) NOT NULL DEFAULT 'standalone', "
                    "user_id VARCHAR(128) NOT NULL DEFAULT 'standalone', "
                    "hook_id VARCHAR(36) NOT NULL, created_at VARCHAR(40) NOT NULL, "
                    "PRIMARY KEY (tenant_id, user_id, hook_id))"
                )
            )
            tenant_expression = "tenant_id" if "tenant_id" in favorite_columns else "'standalone'"
            user_expression = "user_id" if "user_id" in favorite_columns else "'standalone'"
            connection.execute(
                text(
                    "INSERT INTO favorites_migrated (tenant_id, user_id, hook_id, created_at) "
                    f"SELECT {tenant_expression}, {user_expression}, hook_id, created_at FROM favorites"
                )
            )
            connection.execute(text("DROP TABLE favorites"))
            connection.execute(text("ALTER TABLE favorites_migrated RENAME TO favorites"))


def create_database(url: str) -> Engine:
    """Create an initialized SQLite 2.x engine with FK enforcement.

    In-memory databases use one process-local connection through ``StaticPool`` so
    their contents survive normal connect/begin boundaries. File databases allow
    SQLAlchemy to choose its SQLite-safe thread settings.
    """
    if not isinstance(url, str) or not url.strip():
        raise TypeError("database URL must be a non-empty SQLite URL string")
    parsed = None
    try:
        parsed = make_url(url)
    except ArgumentError:
        pass
    if parsed is None:
        # Raise outside the handler so the parser error (which can contain the URL)
        # is neither chained nor retained as ``__context__``.
        raise ValueError("invalid SQLite database URL")
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
        _backup_legacy_file(parsed.database)
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
                owner = threading.get_ident()
                if pool.connection_owner != owner:
                    pool.connection_lock.acquire()
                    pool.connection_owner = owner

            @event.listens_for(pool, "checkin")
            def _serialize_checkin(*_args: Any) -> None:
                if pool.connection_owner == threading.get_ident():
                    pool.connection_owner = None
                    pool.connection_lock.release()

        @event.listens_for(engine, "connect")
        def _enable_foreign_keys(dbapi_connection: Any, _connection_record: Any) -> None:
            cursor = dbapi_connection.cursor()
            try:
                cursor.execute("PRAGMA foreign_keys=ON")
            finally:
                cursor.close()

        metadata.create_all(engine)
        _migrate_legacy_schema(engine)
    except Exception:  # noqa: BLE001 - all initialization failures share a safe API error
        initialization_failed = True
    else:
        initialization_failed = False

    if initialization_failed:
        if engine is not None:
            try:
                engine.dispose()
            except Exception:  # noqa: BLE001, S110 - preserve the sanitized API error
                pass
        # This is deliberately outside both exception handlers: ``from None`` only
        # suppresses display and would still retain a potentially secret-bearing error.
        raise RuntimeError("failed to initialize SQLite database")
    return engine
