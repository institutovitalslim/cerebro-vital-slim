"""Strict public schemas for the versioned HTTP API."""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictInt,
    StringConstraints,
)

from hook_intelligence.domain.models import (
    Channel,
    ComplianceResult,
    GenerationRequest,
    GenerationResponse,
    Hook,
    HookScores,
    Library,
)

PublicText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)]
TopicText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=300)]
WorkspaceRef = Annotated[str, StringConstraints(min_length=1, max_length=256)]
GenerationWord = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
]


class APISchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class GenerateRequest(GenerationRequest):
    intensity: Annotated[StrictInt, Field(ge=1, le=3)] = 2
    mechanism: GenerationWord | None = None
    required_words: list[GenerationWord] = Field(default_factory=list, max_length=50)
    forbidden_words: list[GenerationWord] = Field(default_factory=list, max_length=50)
    count: Annotated[StrictInt, Field(ge=1, le=50)] = 12
    max_length: Annotated[StrictInt, Field(ge=30, le=280)] = 180
    use_ai: StrictBool = False

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "topic": "qualidade do sono",
                    "channel": "reel",
                    "objective": "retention",
                    "audience": "mulheres acima de 40",
                    "library": "universal",
                    "count": 5,
                    "use_ai": False,
                }
            ]
        },
    )


class GenerateResponse(GenerationResponse):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "request_id": "9b49cc6c-7fae-48a8-a1be-e95197534983",
                    "hooks": [],
                    "warnings": [],
                    "engine_version": "0.1.0",
                    "duration_ms": 1.2,
                }
            ]
        },
    )


class ScoreRequest(APISchema):
    text: PublicText
    channel: Channel
    topic: TopicText

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "text": "3 sinais sobre qualidade do sono",
                    "channel": "reel",
                    "topic": "qualidade do sono",
                }
            ]
        },
    )


class ScoreResponse(HookScores):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "clarity": 80,
                    "specificity": 75,
                    "novelty": 70,
                    "retention": 85,
                    "channel_fit": 90,
                    "overall": 80,
                }
            ]
        },
    )


class ComplianceRequest(APISchema):
    text: PublicText
    library: Library

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [{"text": "Conteúdo educativo sobre saúde.", "library": "ivs-health"}]
        },
    )


class ComplianceResponse(ComplianceResult):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"examples": [{"status": "pass", "reasons": []}]},
    )


class FavoriteResponse(APISchema):
    id: UUID
    favorite: bool = True

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [{"id": "a67621f1-ceaa-4053-958c-4bf629246a06", "favorite": True}]
        },
    )


class HistoryItem(APISchema):
    request_id: UUID
    created_at: datetime
    hook_count: int = Field(ge=0)


class HistoryPage(APISchema):
    items: list[HistoryItem]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"examples": [{"items": [], "total": 0, "page": 1, "page_size": 20}]},
    )


class FavoritesPage(APISchema):
    items: list[Hook]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"examples": [{"items": [], "total": 0, "page": 1, "page_size": 20}]},
    )


class TaxonomiesResponse(APISchema):
    taxonomies: dict[str, list[str]]
    mechanisms: list[str]

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {"taxonomies": {"channels": ["reel", "email"]}, "mechanisms": ["curiosity_gap"]}
            ]
        },
    )


class PatternResponse(APISchema):
    id: str
    library: Library
    mechanism: str
    objectives: list[str]
    channels: list[str]
    awareness_stages: list[str]
    tones: list[str]
    template: str
    slots: list[str]
    explanation: str
    intensity: int = Field(ge=1, le=3)


class PatternsResponse(APISchema):
    items: list[PatternResponse]
    total: int = Field(ge=0)

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"examples": [{"items": [], "total": 0}]},
    )


class ExportRequest(APISchema):
    session_id: UUID
    workspace_ref: WorkspaceRef

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "session_id": "9b49cc6c-7fae-48a8-a1be-e95197534983",
                    "workspace_ref": "ivs-internal",
                }
            ]
        },
    )


class ExportHook(Hook):
    favorite: bool = False


class ExportResponse(APISchema):
    schema_version: Literal["1.0.0"] = "1.0.0"
    workspace_ref: str
    generated_at: AwareDatetime
    hooks: list[ExportHook]

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "schema_version": "1.0.0",
                    "workspace_ref": "ivs-internal",
                    "generated_at": "2026-01-02T03:04:05Z",
                    "hooks": [],
                }
            ]
        },
    )


class ErrorResponse(APISchema):
    detail: str

    model_config = ConfigDict(
        extra="forbid", json_schema_extra={"examples": [{"detail": "resource not found"}]}
    )
