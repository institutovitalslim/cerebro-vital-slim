"""Pure, contract-validated JSON and spreadsheet-safe CSV exporters."""

from __future__ import annotations

import csv
import io
import json
import re
import unicodedata
from collections.abc import Collection, Mapping, Sequence
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any
from uuid import UUID

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from hook_intelligence.domain.models import ComplianceStatus, Hook

_CONTRACTS = Path(__file__).parents[3] / "contracts"

# Defensive, non-streaming export envelope. These values intentionally accommodate
# the normal 1,000-hook probe while rejecting pathological input before serialization.
MAX_EXPORT_HOOKS = 1_000
MAX_TEXT_LENGTH = 4_096
MAX_INTERNAL_COLLECTION = 64
MAX_TOTAL_TEXT_CHARACTERS = 2_000_000

CSV_HEADER = (
    "id",
    "text",
    "library",
    "pattern_id",
    "mechanisms",
    "objective",
    "channel",
    "audience",
    "topic",
    "tone",
    "overall_score",
    "compliance_status",
    "compliance_reasons",
    "explanation",
    "source",
    "engine_version",
    "created_at",
    "favorite",
)
_FORMULA_PREFIX = re.compile(r"^(\s*)[=+\-@]")
_RFC3339_DATE_TIME = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
    r"(?:\.\d+)?(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)$"
)
_DATE_TIME_CHECKER = FormatChecker()


@_DATE_TIME_CHECKER.checks("date-time")
def _is_rfc3339_datetime(value: object) -> bool:
    """Check strict RFC3339 date-time syntax, calendar values, and mandatory offset."""
    if not isinstance(value, str):
        return True  # JSON Schema's type keyword owns type diagnostics.
    if _RFC3339_DATE_TIME.fullmatch(value) is None:
        return False
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def _check_text(value: str, path: str, *, csv_controls: bool = False) -> int:
    if len(value) > MAX_TEXT_LENGTH:
        raise ValueError(f"{path} must not exceed {MAX_TEXT_LENGTH} characters")
    if csv_controls and any(
        unicodedata.category(character).startswith("C") and character not in "\t\r\n"
        for character in value
    ):
        raise ValueError(f"{path} contains a prohibited Unicode category C character")
    return len(value)


def _hook_text_fields(item: Hook, index: int):
    prefix = f"hooks[{index}]"
    for name in ("text", "pattern_id", "audience", "topic", "explanation"):
        yield f"{prefix}.{name}", getattr(item, name)
    for position, value in enumerate(item.mechanisms):
        yield f"{prefix}.mechanisms[{position}]", value
    for position, value in enumerate(item.compliance.reasons):
        yield f"{prefix}.compliance.reasons[{position}]", value


def _validate_hooks(values: Sequence[Hook], *, csv_controls: bool = False) -> tuple[Hook, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise TypeError("hooks must be a sequence of Hook values")
    if len(values) > MAX_EXPORT_HOOKS:
        raise ValueError(f"hooks must not contain more than {MAX_EXPORT_HOOKS} items")

    hooks: list[Hook] = []
    total_text = 0
    for index, item in enumerate(values):
        if not isinstance(item, Hook):
            raise TypeError("hooks must contain only Hook values")
        if len(item.mechanisms) > MAX_INTERNAL_COLLECTION:
            raise ValueError(
                f"hooks[{index}].mechanisms must not contain more than "
                f"{MAX_INTERNAL_COLLECTION} items"
            )
        if len(item.compliance.reasons) > MAX_INTERNAL_COLLECTION:
            raise ValueError(
                f"hooks[{index}].compliance.reasons must not contain more than "
                f"{MAX_INTERNAL_COLLECTION} items"
            )
        if item.compliance.status is ComplianceStatus.BLOCK:
            raise ValueError("compliance BLOCK hooks cannot be exported")
        for path, text in _hook_text_fields(item, index):
            total_text += _check_text(text, path, csv_controls=csv_controls)
            if total_text > MAX_TOTAL_TEXT_CHARACTERS:
                raise ValueError(
                    f"export text must not exceed {MAX_TOTAL_TEXT_CHARACTERS} characters"
                )
        hooks.append(item)
    return tuple(hooks)


def _favorite_strings(values: Collection[UUID | str] | None) -> set[str]:
    if values is None:
        return set()
    if isinstance(values, (str, bytes)) or not isinstance(values, Collection):
        raise TypeError("favorites must be a collection of hook IDs")
    if len(values) > MAX_EXPORT_HOOKS:
        raise ValueError(f"favorites must not contain more than {MAX_EXPORT_HOOKS} items")
    normalized = set()
    for index, value in enumerate(values):
        if isinstance(value, bool) or not isinstance(value, (UUID, str)):
            raise TypeError(f"favorites[{index}] must be a UUID or UUID string")
        try:
            normalized.add(str(UUID(str(value))))
        except (ValueError, AttributeError) as exc:
            raise ValueError(f"invalid favorites[{index}]: {value!r}") from exc
    return normalized


def _workspace_ref(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("workspace_ref must be a string")
    normalized = unicodedata.normalize("NFKC", value)
    if not 1 <= len(normalized) <= 256:
        raise ValueError("workspace_ref must contain between 1 and 256 characters")
    if normalized != normalized.strip():
        raise ValueError("workspace_ref must not have leading or trailing whitespace")
    if any(unicodedata.category(character).startswith("C") for character in normalized):
        raise ValueError("workspace_ref must not contain Unicode control characters")
    if not any(character.isalnum() for character in normalized):
        raise ValueError("workspace_ref must contain at least one alphanumeric character")
    return normalized


def make_export_payload(
    hooks: Sequence[Hook],
    workspace_ref: str,
    *,
    favorites: Collection[UUID | str] | None = None,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    """Build and validate a JSON-compatible Content OS export payload."""
    checked = _validate_hooks(hooks)
    safe_workspace_ref = _workspace_ref(workspace_ref)
    timestamp = generated_at or datetime.now(UTC)
    if not isinstance(timestamp, datetime):
        raise TypeError("generated_at must be a datetime")
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("generated_at must include a timezone")
    favorite_ids = _favorite_strings(favorites)
    exported_hooks = []
    for item in checked:
        value = item.model_dump(mode="json")
        value["created_at"] = item.created_at.astimezone(UTC).isoformat().replace("+00:00", "Z")
        value["favorite"] = str(item.id) in favorite_ids
        exported_hooks.append(value)
    payload = {
        "schema_version": "1.0.0",
        "workspace_ref": safe_workspace_ref,
        "generated_at": timestamp.astimezone(UTC).isoformat().replace("+00:00", "Z"),
        "hooks": exported_hooks,
    }
    validate_export_payload(payload)
    return payload


@lru_cache(maxsize=1)
def _validator() -> Draft202012Validator:
    hook_schema = json.loads((_CONTRACTS / "hook.schema.json").read_text(encoding="utf-8"))
    export_schema = json.loads(
        (_CONTRACTS / "content-os-export.schema.json").read_text(encoding="utf-8")
    )
    registry = Registry().with_resource(hook_schema["$id"], Resource.from_contents(hook_schema))
    return Draft202012Validator(
        export_schema,
        registry=registry,
        format_checker=_DATE_TIME_CHECKER,
    )


def _preflight_payload(payload: Any) -> None:
    """Bound arbitrary JSON-like input iteratively before deep schema validation."""
    active: set[int] = set()
    total_text = 0
    stack: list[tuple[Any, str, bool]] = [(payload, "$", False)]

    while stack:
        value, path, exiting = stack.pop()
        if exiting:
            active.remove(id(value))
            continue
        if isinstance(value, str):
            total_text += _check_text(value, path)
            if total_text > MAX_TOTAL_TEXT_CHARACTERS:
                raise ValueError(
                    f"export text must not exceed {MAX_TOTAL_TEXT_CHARACTERS} characters"
                )
            continue
        if isinstance(value, Mapping):
            identity = id(value)
            if identity in active:
                raise ValueError(f"cycle detected in export payload at {path}")
            if len(value) > MAX_INTERNAL_COLLECTION:
                raise ValueError(
                    f"{path} must not contain more than {MAX_INTERNAL_COLLECTION} entries"
                )
            active.add(identity)
            stack.append((value, path, True))
            for key, child in reversed(tuple(value.items())):
                # Keys are textual content too, but schema remains responsible for key types.
                if isinstance(key, str):
                    stack.append((child, f"{path}.{key}", False))
                    stack.append((key, f"{path}.<key>", False))
                else:
                    stack.append((child, f"{path}.<key>", False))
            continue
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            identity = id(value)
            if identity in active:
                raise ValueError(f"cycle detected in export payload at {path}")
            maximum = MAX_EXPORT_HOOKS if path == "$.hooks" else MAX_INTERNAL_COLLECTION
            if len(value) > maximum:
                raise ValueError(f"{path} must not contain more than {maximum} items")
            active.add(identity)
            stack.append((value, path, True))
            for index in range(len(value) - 1, -1, -1):
                stack.append((value[index], f"{path}[{index}]", False))


def validate_export_payload(payload: Any) -> None:
    """Raise ``jsonschema.ValidationError`` unless payload matches the real contract."""
    _preflight_payload(payload)
    _validator().validate(payload)
    for item in payload["hooks"]:
        if item["compliance"]["status"] == ComplianceStatus.BLOCK:
            raise ValueError("compliance BLOCK hooks cannot be exported")


def export_json(payload: dict[str, Any]) -> str:
    """Validate and encode JSON as a Unicode-preserving string."""
    validate_export_payload(payload)
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _safe_cell(value: Any) -> str:
    text = str(value)
    # Preserve leading whitespace while inserting an apostrophe immediately before
    # formula markers. Spreadsheet applications then treat the cell as literal text.
    return _FORMULA_PREFIX.sub(
        lambda match: f"{match.group(1)}'{text[len(match.group(1))]}", text, count=1
    )


def export_csv(hooks: Sequence[Hook], *, favorites: Collection[UUID | str] | None = None) -> str:
    """Encode hooks in deterministic order as RFC4180 CSV with formula protection."""
    checked = _validate_hooks(hooks, csv_controls=True)
    favorite_ids = _favorite_strings(favorites)
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\r\n")
    writer.writerow(CSV_HEADER)
    for item in checked:
        writer.writerow(
            (
                str(item.id),
                _safe_cell(item.text),
                item.library.value,
                _safe_cell(item.pattern_id),
                "|".join(_safe_cell(value) for value in item.mechanisms),
                item.objective.value,
                item.channel.value,
                _safe_cell(item.audience),
                _safe_cell(item.topic),
                item.tone.value,
                item.scores.overall,
                item.compliance.status.value,
                "|".join(_safe_cell(value) for value in item.compliance.reasons),
                _safe_cell(item.explanation),
                item.source.value,
                item.engine_version,
                item.created_at.astimezone(UTC).isoformat().replace("+00:00", "Z"),
                "true" if str(item.id) in favorite_ids else "false",
            )
        )
    return output.getvalue()
