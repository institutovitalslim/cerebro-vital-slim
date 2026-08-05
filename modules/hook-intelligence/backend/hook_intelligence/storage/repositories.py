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

_STANDALONE_ID = "standalone"


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


def _owner(tenant_id: str, user_id: str) -> tuple[str, str]:
    for value, label in ((tenant_id, "tenant_id"), (user_id, "user_id")):
        if not isinstance(value, str) or not value or len(value) > 128:
            raise ValueError(f"{label} must be a non-empty string of at most 128 characters")
    return tenant_id, user_id


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
    """Transactional history and favorites isolated by tenant and user ownership."""

    def __init__(self, engine: Engine) -> None:
        if not isinstance(engine, Engine):
            raise TypeError("HookRepository requires a SQLAlchemy Engine")
        if engine.dialect.name != "sqlite":
            raise ValueError("HookRepository supports only SQLite engines")
        self._engine = engine

    def save_generation(
        self,
        generation: Sequence[Hook],
        *,
        tenant_id: str = _STANDALONE_ID,
        user_id: str = _STANDALONE_ID,
    ) -> str:
        tenant_id, user_id = _owner(tenant_id, user_id)
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
                {
                    "session_id": session_id,
                    "tenant_id": tenant_id,
                    "user_id": user_id,
                    "created_at": _utc_text(),
                },
            )
            for position, item in enumerate(generation):
                value = item.model_dump(mode="json")
                value["created_at"] = _utc_text(item.created_at)
                connection.execute(
                    insert(hooks),
                    {
                        "session_id": session_id,
                        "tenant_id": tenant_id,
                        "user_id": user_id,
                        "position": position,
                        "hook_id": value.pop("id"),
                        **value,
                    },
                )
        return session_id

    def get_session(
        self,
        session_id: UUID | str,
        *,
        tenant_id: str = _STANDALONE_ID,
        user_id: str = _STANDALONE_ID,
    ) -> tuple[Hook, ...]:
        identifier = _uuid_text(session_id, label="session_id")
        tenant_id, user_id = _owner(tenant_id, user_id)
        owner_filter = (
            generation_sessions.c.tenant_id == tenant_id,
            generation_sessions.c.user_id == user_id,
        )
        with self._engine.connect() as connection:
            exists = connection.execute(
                select(generation_sessions.c.row_id).where(
                    generation_sessions.c.session_id == identifier, *owner_filter
                )
            ).first()
            if exists is None:
                raise LookupError(f"generation session {identifier} does not exist")
            try:
                rows = connection.execute(
                    select(hooks)
                    .where(
                        hooks.c.session_id == identifier,
                        hooks.c.tenant_id == tenant_id,
                        hooks.c.user_id == user_id,
                    )
                    .order_by(hooks.c.position)
                ).all()
            except (JSONDecodeError, StatementError) as exc:
                raise ValueError(f"invalid persisted Hook payload in session {identifier}") from exc
        return tuple(_row_to_hook(row) for row in rows)

    def get_hook(
        self,
        hook_id: UUID | str,
        *,
        tenant_id: str = _STANDALONE_ID,
        user_id: str = _STANDALONE_ID,
    ) -> Hook:
        identifier = _uuid_text(hook_id, label="hook_id")
        tenant_id, user_id = _owner(tenant_id, user_id)
        with self._engine.connect() as connection:
            try:
                row = connection.execute(
                    select(hooks)
                    .where(
                        hooks.c.hook_id == identifier,
                        hooks.c.tenant_id == tenant_id,
                        hooks.c.user_id == user_id,
                    )
                    .order_by(hooks.c.row_id.desc())
                    .limit(1)
                ).first()
            except (JSONDecodeError, StatementError) as exc:
                raise ValueError(f"invalid persisted Hook payload for hook {identifier}") from exc
        if row is None:
            raise LookupError(f"hook {identifier} does not exist in history")
        return _row_to_hook(row)

    def list_sessions(
        self,
        page: int = 1,
        page_size: int = 20,
        *,
        tenant_id: str = _STANDALONE_ID,
        user_id: str = _STANDALONE_ID,
    ) -> dict[str, Any]:
        self._validate_page_value(page, "page")
        self._validate_page_value(page_size, "page_size", maximum=100)
        tenant_id, user_id = _owner(tenant_id, user_id)
        owner_filter = (
            generation_sessions.c.tenant_id == tenant_id,
            generation_sessions.c.user_id == user_id,
        )
        with self._engine.connect() as connection:
            total = connection.execute(
                select(func.count()).select_from(generation_sessions).where(*owner_filter)
            ).scalar_one()
            statement = (
                select(
                    generation_sessions.c.session_id,
                    generation_sessions.c.created_at,
                    func.count(hooks.c.row_id).label("hook_count"),
                )
                .outerjoin(
                    hooks,
                    (hooks.c.session_id == generation_sessions.c.session_id)
                    & (hooks.c.tenant_id == tenant_id)
                    & (hooks.c.user_id == user_id),
                )
                .where(*owner_filter)
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

    def favorite(
        self,
        hook_id: UUID | str,
        *,
        tenant_id: str = _STANDALONE_ID,
        user_id: str = _STANDALONE_ID,
    ) -> None:
        identifier = _uuid_text(hook_id, label="hook_id")
        tenant_id, user_id = _owner(tenant_id, user_id)
        favorite_filter = (
            favorites.c.hook_id == identifier,
            favorites.c.tenant_id == tenant_id,
            favorites.c.user_id == user_id,
        )
        with self._engine.begin() as connection:
            if connection.execute(select(favorites.c.hook_id).where(*favorite_filter)).first():
                return
            if (
                connection.execute(
                    select(hooks.c.row_id)
                    .where(
                        hooks.c.hook_id == identifier,
                        hooks.c.tenant_id == tenant_id,
                        hooks.c.user_id == user_id,
                    )
                    .limit(1)
                ).first()
                is None
            ):
                raise LookupError(f"hook {identifier} does not exist in history")
            connection.execute(
                sqlite_insert(favorites)
                .values(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    hook_id=identifier,
                    created_at=_utc_text(),
                )
                .on_conflict_do_nothing(
                    index_elements=[favorites.c.tenant_id, favorites.c.user_id, favorites.c.hook_id]
                )
            )

    def unfavorite(
        self,
        hook_id: UUID | str,
        *,
        tenant_id: str = _STANDALONE_ID,
        user_id: str = _STANDALONE_ID,
    ) -> None:
        identifier = _uuid_text(hook_id, label="hook_id")
        tenant_id, user_id = _owner(tenant_id, user_id)
        with self._engine.begin() as connection:
            connection.execute(
                delete(favorites).where(
                    favorites.c.hook_id == identifier,
                    favorites.c.tenant_id == tenant_id,
                    favorites.c.user_id == user_id,
                )
            )

    def is_favorite(
        self,
        hook_id: UUID | str,
        *,
        tenant_id: str = _STANDALONE_ID,
        user_id: str = _STANDALONE_ID,
    ) -> bool:
        identifier = _uuid_text(hook_id, label="hook_id")
        tenant_id, user_id = _owner(tenant_id, user_id)
        with self._engine.connect() as connection:
            return (
                connection.execute(
                    select(favorites.c.hook_id).where(
                        favorites.c.hook_id == identifier,
                        favorites.c.tenant_id == tenant_id,
                        favorites.c.user_id == user_id,
                    )
                ).first()
                is not None
            )

    def list_favorites(
        self,
        page: int = 1,
        page_size: int = 20,
        *,
        tenant_id: str = _STANDALONE_ID,
        user_id: str = _STANDALONE_ID,
    ) -> dict[str, Any]:
        """List each favorited logical hook once within its owner scope."""

        self._validate_page_value(page, "page")
        self._validate_page_value(page_size, "page_size", maximum=100)
        tenant_id, user_id = _owner(tenant_id, user_id)
        latest_hook = hooks.alias("latest_hook")
        latest_row = (
            select(func.max(latest_hook.c.row_id))
            .where(
                latest_hook.c.hook_id == favorites.c.hook_id,
                latest_hook.c.tenant_id == tenant_id,
                latest_hook.c.user_id == user_id,
            )
            .scalar_subquery()
        )
        favorite_filter = (
            favorites.c.tenant_id == tenant_id,
            favorites.c.user_id == user_id,
        )
        with self._engine.connect() as connection:
            total = connection.execute(
                select(func.count()).select_from(favorites).where(*favorite_filter)
            ).scalar_one()
            statement = (
                select(hooks)
                .join(
                    favorites,
                    (favorites.c.hook_id == hooks.c.hook_id)
                    & (favorites.c.tenant_id == hooks.c.tenant_id)
                    & (favorites.c.user_id == hooks.c.user_id),
                )
                .where(
                    *favorite_filter,
                    hooks.c.tenant_id == tenant_id,
                    hooks.c.user_id == user_id,
                    hooks.c.row_id == latest_row,
                )
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

    def export_session(
        self,
        session_id: UUID | str,
        workspace_ref: str,
        *,
        tenant_id: str = _STANDALONE_ID,
        user_id: str = _STANDALONE_ID,
    ) -> dict[str, Any]:
        tenant_id, user_id = _owner(tenant_id, user_id)
        session_hooks = self.get_session(session_id, tenant_id=tenant_id, user_id=user_id)
        identifiers = [str(item.id) for item in session_hooks]
        with self._engine.connect() as connection:
            favorite_ids = set(
                connection.execute(
                    select(favorites.c.hook_id).where(
                        favorites.c.hook_id.in_(identifiers),
                        favorites.c.tenant_id == tenant_id,
                        favorites.c.user_id == user_id,
                    )
                ).scalars()
            )
        return make_export_payload(session_hooks, workspace_ref, favorites=favorite_ids)
