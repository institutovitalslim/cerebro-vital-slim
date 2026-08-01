"""Contrato e validação auditável do handoff Content Radar -> geração.

O payload recebido da UI não é evidência suficiente por si só. Antes de uma peça
ser persistida, os IDs são resolvidos em uma única cadeia pertencente ao tenant:
item externo -> snapshot candidato -> baseline/version/cutoff.
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any
from urllib.parse import urlsplit

from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator, model_validator

_UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$")
_EXTERNAL_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:@/-]{0,299}$")
_VERSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")
_RADAR_FIELDS = (
    "radar_item_id",
    "radar_external_id",
    "radar_baseline_id",
    "radar_snapshot_id",
    "radar_cutoff_at",
    "radar_algorithm_version",
)


class RadarProvenanceMixin(BaseModel):
    """Campos planos compatíveis com a query string do Radar.

    As subclasses precisam declarar ``source``. Proveniência parcial é rejeitada:
    uma auditoria não pode depender de um subconjunto ambíguo de identificadores.
    """

    radar_item_id: str | None = None
    radar_external_id: str | None = Field(default=None, max_length=300)
    radar_baseline_id: str | None = None
    radar_snapshot_id: str | None = None
    radar_cutoff_at: datetime | None = None
    radar_algorithm_version: str | None = Field(default=None, max_length=80)

    @field_validator("radar_item_id", "radar_baseline_id", "radar_snapshot_id")
    @classmethod
    def validate_uuid(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not _UUID_RE.fullmatch(value):
            raise ValueError("ID de proveniência Radar deve ser UUID canônico")
        return value.lower()

    @field_validator("radar_external_id")
    @classmethod
    def validate_external_id(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("radar_external_id não pode ser vazio")
        if "://" in value:
            parsed = urlsplit(value)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.username or parsed.password:
                raise ValueError("radar_external_id contém URL malformada")
        elif not _EXTERNAL_ID_RE.fullmatch(value):
            raise ValueError("radar_external_id malformado")
        return value

    @field_validator("radar_algorithm_version")
    @classmethod
    def validate_algorithm_version(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not _VERSION_RE.fullmatch(value):
            raise ValueError("radar_algorithm_version malformada")
        return value

    @field_validator("radar_cutoff_at")
    @classmethod
    def validate_cutoff(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("radar_cutoff_at deve incluir fuso horário")
        return value

    @model_validator(mode="after")
    def validate_complete_radar_handoff(self):
        values = [getattr(self, field) for field in _RADAR_FIELDS]
        if not any(value is not None for value in values):
            return self
        if getattr(self, "source", None) != "radar":
            raise ValueError("proveniência Radar exige source=radar")
        missing = [field for field, value in zip(_RADAR_FIELDS, values) if value is None]
        if missing:
            raise ValueError(f"proveniência Radar incompleta: {', '.join(missing)}")
        return self


def radar_provenance(payload: RadarProvenanceMixin) -> dict[str, str]:
    """Normaliza o objeto JSONB canônico; vazio mantém consumidores legados."""

    if payload.radar_item_id is None:
        return {}
    cutoff = payload.radar_cutoff_at
    assert cutoff is not None  # garantido pelo validator do modelo
    return {
        "source": "radar",
        "radar_item_id": payload.radar_item_id,
        "radar_external_id": payload.radar_external_id or "",
        "radar_baseline_id": payload.radar_baseline_id or "",
        "radar_snapshot_id": payload.radar_snapshot_id or "",
        "radar_cutoff_at": cutoff.isoformat(),
        "radar_algorithm_version": payload.radar_algorithm_version or "",
    }


def validate_radar_tenant_chain(conn: Any, tenant_id: str, provenance: dict[str, str]) -> None:
    """Rejeita IDs válidos sintaticamente, mas alheios/inconsistentes no tenant.

    A consulta também impede misturar snapshot/baseline de itens diferentes ou
    adulterar external_id, cutoff e versão do algoritmo no handoff.
    """

    if not provenance:
        return
    with conn.cursor() as cur:
        cur.execute(
            """
            select 1
            from external_content_items e
            join external_metric_snapshots s
              on s.id=%s and s.tenant_id=e.tenant_id and s.content_item_id=e.id
            join external_content_baselines b
              on b.id=%s and b.tenant_id=e.tenant_id
             and b.candidate_content_item_id=e.id
             and b.candidate_metric_snapshot_id=s.id
            where e.id=%s and e.tenant_id=%s and e.external_id=%s
              and b.cutoff_at=%s and b.algorithm_version=%s
            """,
            (
                provenance["radar_snapshot_id"],
                provenance["radar_baseline_id"],
                provenance["radar_item_id"],
                tenant_id,
                provenance["radar_external_id"],
                provenance["radar_cutoff_at"],
                provenance["radar_algorithm_version"],
            ),
        )
        if not cur.fetchone():
            raise HTTPException(
                status_code=422,
                detail="proveniência Radar não pertence ao tenant ou não forma uma cadeia auditável",
            )
