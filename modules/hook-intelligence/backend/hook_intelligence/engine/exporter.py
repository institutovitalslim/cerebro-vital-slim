"""Pure, contract-validated JSON and spreadsheet-safe CSV exporters."""

from __future__ import annotations

import csv
import io
import json
import re
import unicodedata
from collections.abc import Collection, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from hook_intelligence.domain.models import ComplianceStatus, Hook

_CONTRACTS = Path(__file__).parents[3] / "contracts"
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


def _validate_hooks(values: Sequence[Hook]) -> tuple[Hook, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise TypeError("hooks must be a sequence of Hook values")
    hooks = tuple(values)
    if any(not isinstance(item, Hook) for item in hooks):
        raise TypeError("hooks must contain only Hook values")
    if any(item.compliance.status is ComplianceStatus.BLOCK for item in hooks):
        raise ValueError("compliance BLOCK hooks cannot be exported")
    return hooks


def _favorite_strings(values: Collection[UUID | str] | None) -> set[str]:
    if values is None:
        return set()
    if isinstance(values, (str, bytes)) or not isinstance(values, Collection):
        raise TypeError("favorites must be a collection of hook IDs")
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


def _validator() -> Draft202012Validator:
    hook_schema = json.loads((_CONTRACTS / "hook.schema.json").read_text(encoding="utf-8"))
    export_schema = json.loads(
        (_CONTRACTS / "content-os-export.schema.json").read_text(encoding="utf-8")
    )
    registry = Registry().with_resource(hook_schema["$id"], Resource.from_contents(hook_schema))
    return Draft202012Validator(
        export_schema,
        registry=registry,
        format_checker=FormatChecker(),
    )


def validate_export_payload(payload: Any) -> None:
    """Raise ``jsonschema.ValidationError`` unless payload matches the real contract."""
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
    """Encode hooks in deterministic order as RFC-style CSV with formula protection."""
    checked = _validate_hooks(hooks)
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
