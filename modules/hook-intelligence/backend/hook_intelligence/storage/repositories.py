"""Persistence repositories."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from json import JSONDecodeError
from typing import Any
from uuid import UUID, uuid4

from pydantic import ValidationError
from sqlalchemy import delete, func, insert, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import Engine
from sqlalchemy.exc import StatementError

from hook_intelligence.domain.models import ComplianceStatus, Hook
from hook_intelligence.engine.exporter import make_export_payload
from hook_intelligence.storage.database import favorites, generation_sessions, hooks


def _utc_text(value: datetime | None = None) -> str:
    current = value or datetime.now(UTC)
    if current.tzinfo is None or current.utcoffset() is None:
        raise ValueError("timestamp must include a UTC offset")
    return current.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _uuid_text(value: UUID | str, *, label: str) -> str:
    if isinstance(value, bool) or not isinstance(value, (UUID, str)):
        raise TypeError(f"{label} must be a UUID or UUID string")
    try:
        return str(UUID(str(value)))
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"invalid {label}: {value!r}") from exc


def _row_to_hook(row: Any) -> Hook:
    data = {
        "id": row.hook_id,
        "text": row.text,
        "language": row.language,
        "library": row.library,
        "pattern_id": row.pattern_id,
        "mechanisms": row.mechanisms,
        "objective": row.objective,
        "channel": row.channel,
        "awareness_stage": row.awareness_stage,
        "audience": row.audience,
        "topic": row.topic,
        "tone": row.tone,
        "scores": row.scores,
        "compliance": row.compliance,
        "explanation": row.explanation,
        "source": row.source,
        "engine_version": row.engine_version,
        "created_at": row.created_at,
    }
    try:
        return Hook.model_validate(data)
    except ValidationError as exc:
        raise ValueError(f"invalid persisted Hook payload for hook {row.hook_id}") from exc


class HookRepository:
    """Transactional history and global logical-hook favorites."""

    def __init__(self, engine: Engine) -> None:
        if not isinstance(engine, Engine):
            raise TypeError("HookRepository requires a SQLAlchemy Engine")
        if engine.dialect.name != "sqlite":
            raise ValueError("HookRepository supports only SQLite engines")
        self._engine = engine

    def save_generation(self, generation: Sequence[Hook]) -> str:
        if isinstance(generation, (str, bytes)) or not isinstance(generation, Sequence):
            raise TypeError("generation must be a non-empty sequence of Hook values")
        if not generation:
            raise ValueError("generation must be non-empty")
        if any(not isinstance(item, Hook) for item in generation):
            raise TypeError("generation must contain only Hook values")
        ids = [str(item.id) for item in generation]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate hook.id in generation")
        if any(item.compliance.status is ComplianceStatus.BLOCK for item in generation):
            raise ValueError("generation containing compliance BLOCK cannot be persisted")

        session_id = str(uuid4())
        with self._engine.begin() as connection:
            connection.execute(
                insert(generation_sessions),
                {"session_id": session_id, "created_at": _utc_text()},
            )
            for position, item in enumerate(generation):
                value = item.model_dump(mode="json")
                value["created_at"] = _utc_text(item.created_at)
                connection.execute(
                    insert(hooks),
                    {
                        "session_id": session_id,
                        "position": position,
                        "hook_id": value.pop("id"),
                        **value,
                    },
                )
        return session_id

    def get_session(self, session_id: UUID | str) -> tuple[Hook, ...]:
        identifier = _uuid_text(session_id, label="session_id")
        with self._engine.connect() as connection:
            exists = connection.execute(
                select(generation_sessions.c.row_id).where(
                    generation_sessions.c.session_id == identifier
                )
            ).first()
            if exists is None:
                raise LookupError(f"generation session {identifier} does not exist")
            try:
                rows = connection.execute(
                    select(hooks).where(hooks.c.session_id == identifier).order_by(hooks.c.position)
                ).all()
            except (JSONDecodeError, StatementError) as exc:
                raise ValueError(f"invalid persisted Hook payload in session {identifier}") from exc
        return tuple(_row_to_hook(row) for row in rows)

    def list_sessions(self, page: int = 1, page_size: int = 20) -> dict[str, Any]:
        self._validate_page_value(page, "page")
        self._validate_page_value(page_size, "page_size", maximum=100)
        with self._engine.connect() as connection:
            total = connection.execute(
                select(func.count()).select_from(generation_sessions)
            ).scalar_one()
            statement = (
                select(
                    generation_sessions.c.session_id,
                    generation_sessions.c.created_at,
                    func.count(hooks.c.row_id).label("hook_count"),
                )
                .outerjoin(hooks)
                .group_by(generation_sessions.c.row_id)
                .order_by(generation_sessions.c.row_id.desc())
                .limit(page_size)
                .offset((page - 1) * page_size)
            )
            items = tuple(dict(row._mapping) for row in connection.execute(statement))
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    def _validate_page_value(value: Any, label: str, maximum: int | None = None) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{label} must be an integer")
        if value <= 0:
            raise ValueError(f"{label} must be positive")
        if maximum is not None and value > maximum:
            raise ValueError(f"{label} must not exceed {maximum}")

    def favorite(self, hook_id: UUID | str) -> None:
        identifier = _uuid_text(hook_id, label="hook_id")
        with self._engine.begin() as connection:
            if (
                connection.execute(
                    select(favorites.c.hook_id).where(favorites.c.hook_id == identifier)
                ).first()
                is not None
            ):
                return
            if (
                connection.execute(
                    select(hooks.c.row_id).where(hooks.c.hook_id == identifier).limit(1)
                ).first()
                is None
            ):
                raise LookupError(f"hook {identifier} does not exist in history")
            connection.execute(
                sqlite_insert(favorites)
                .values(hook_id=identifier, created_at=_utc_text())
                .on_conflict_do_nothing(index_elements=[favorites.c.hook_id])
            )

    def unfavorite(self, hook_id: UUID | str) -> None:
        identifier = _uuid_text(hook_id, label="hook_id")
        with self._engine.begin() as connection:
            connection.execute(delete(favorites).where(favorites.c.hook_id == identifier))

    def is_favorite(self, hook_id: UUID | str) -> bool:
        identifier = _uuid_text(hook_id, label="hook_id")
        with self._engine.connect() as connection:
            return (
                connection.execute(
                    select(favorites.c.hook_id).where(favorites.c.hook_id == identifier)
                ).first()
                is not None
            )

    def list_favorites(self, page: int = 1, page_size: int = 20) -> dict[str, Any]:
        """List each globally favorited logical hook once, newest favorite first."""

        self._validate_page_value(page, "page")
        self._validate_page_value(page_size, "page_size", maximum=100)
        latest_hook = hooks.alias("latest_hook")
        latest_row = (
            select(func.max(latest_hook.c.row_id))
            .where(latest_hook.c.hook_id == favorites.c.hook_id)
            .scalar_subquery()
        )
        with self._engine.connect() as connection:
            total = connection.execute(select(func.count()).select_from(favorites)).scalar_one()
            statement = (
                select(hooks)
                .join(favorites, favorites.c.hook_id == hooks.c.hook_id)
                .where(hooks.c.row_id == latest_row)
                .order_by(favorites.c.created_at.desc(), hooks.c.row_id.desc())
                .limit(page_size)
                .offset((page - 1) * page_size)
            )
            try:
                rows = connection.execute(statement).all()
            except (JSONDecodeError, StatementError) as exc:
                raise ValueError("invalid persisted favorite Hook payload") from exc
        return {
            "items": tuple(_row_to_hook(row) for row in rows),
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def export_session(self, session_id: UUID | str, workspace_ref: str) -> dict[str, Any]:
        session_hooks = self.get_session(session_id)
        identifiers = [str(item.id) for item in session_hooks]
        with self._engine.connect() as connection:
            favorite_ids = set(
                connection.execute(
                    select(favorites.c.hook_id).where(favorites.c.hook_id.in_(identifiers))
                ).scalars()
            )
        return make_export_payload(session_hooks, workspace_ref, favorites=favorite_ids)
