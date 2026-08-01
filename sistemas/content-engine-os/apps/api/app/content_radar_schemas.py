"""Contratos tipados para ingestão governada do Content Radar."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Annotated, Literal

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    ConfigDict,
    Field,
    StrictFloat,
    StrictInt,
    computed_field,
    model_validator,
)

from app.content_radar import normalize_format


MetricValue = Annotated[StrictInt | StrictFloat, Field(ge=0, le=1_000_000_000_000_000)]
CollectorSourceKind = Literal["candidate", "thematic_search"]


class RadarMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    views: MetricValue | None = None
    plays: MetricValue | None = None
    reach: MetricValue | None = None
    likes: MetricValue | None = None
    comments: MetricValue | None = None
    shares: MetricValue | None = None
    saves: MetricValue | None = None


class RadarIngestItem(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    source_network: Literal["instagram", "facebook", "youtube", "tiktok", "x"] = "instagram"
    source_profile: str = Field(min_length=1, max_length=200)
    actual_source_profile: str | None = Field(default=None, min_length=1, max_length=200)
    external_id: str | None = Field(default=None, min_length=1, max_length=300)
    url: AnyHttpUrl | None = None
    format: str | None = Field(default=None, max_length=80)
    caption: str | None = Field(default=None, max_length=20_000)
    published_at: datetime | None = None
    observed_at: datetime | None = None
    metrics: RadarMetrics = Field(default_factory=RadarMetrics)
    raw_payload: dict = Field(default_factory=dict)

    @computed_field
    @property
    def canonical_format(self) -> str:
        return normalize_format(self.format)

    @model_validator(mode="after")
    def require_stable_identity(self) -> "RadarIngestItem":
        if not self.external_id and not self.url:
            raise ValueError("external_id ou URL canônica é obrigatório")
        if len(json.dumps(self.raw_payload, ensure_ascii=False, default=str).encode("utf-8")) > 262_144:
            raise ValueError("raw_payload excede 256 KiB")
        return self


class RadarIngestBatch(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    collector_run_id: str = Field(min_length=1, max_length=200)
    source_kind: CollectorSourceKind = "candidate"
    source_display_name: str | None = Field(default=None, max_length=200)
    provider: str = Field(default="unknown", min_length=1, max_length=120)
    observed_at: datetime | None = None
    items: list[RadarIngestItem] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def reject_duplicate_items(self) -> "RadarIngestBatch":
        identities: set[tuple[str, str]] = set()
        for item in self.items:
            if self.source_kind == "thematic_search" and not item.actual_source_profile:
                raise ValueError("actual_source_profile é obrigatório em descoberta temática")
            stable_id = item.external_id or str(item.url).rstrip("/")
            identity = (item.source_network, stable_id.strip().lower())
            if identity in identities:
                raise ValueError("batch contém item externo duplicado")
            identities.add(identity)
        return self
