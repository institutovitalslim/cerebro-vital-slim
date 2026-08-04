from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal
from uuid import UUID, uuid4

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from hook_intelligence import ENGINE_VERSION


class ComplianceStatus(StrEnum):
    PASS = "pass"
    REVIEW = "review"
    BLOCK = "block"


class Channel(StrEnum):
    REEL = "reel"
    AD = "ad"
    CAROUSEL = "carousel"
    STORY = "story"
    LANDING_PAGE = "landing_page"
    EMAIL = "email"
    BLOG = "blog"
    YOUTUBE = "youtube"


class Objective(StrEnum):
    SCROLL_STOP = "scroll_stop"
    CURIOSITY = "curiosity"
    RETENTION = "retention"
    IDENTIFICATION = "identification"
    EDUCATION = "education"
    AUTHORITY = "authority"
    OBJECTION = "objection"
    SHARING = "sharing"
    ACTION = "action"


class Library(StrEnum):
    UNIVERSAL = "universal"
    IVS_HEALTH = "ivs-health"


class AwarenessStage(StrEnum):
    UNAWARE = "unaware"
    PROBLEM_AWARE = "problem_aware"
    SOLUTION_AWARE = "solution_aware"
    PRODUCT_AWARE = "product_aware"
    READY_TO_ACT = "ready_to_act"


class Tone(StrEnum):
    PREMIUM = "premium"
    EDUCATIONAL = "educational"
    DIRECT = "direct"
    EMPATHETIC = "empathetic"
    PROVOCATIVE = "provocative"


class Source(StrEnum):
    DETERMINISTIC = "deterministic"
    AI_ADAPTED = "ai_adapted"
    CURATED = "curated"


class DomainModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class HookScores(DomainModel):
    clarity: float = Field(ge=0, le=100)
    specificity: float = Field(ge=0, le=100)
    novelty: float = Field(ge=0, le=100)
    retention: float = Field(ge=0, le=100)
    channel_fit: float = Field(ge=0, le=100)
    overall: float = Field(ge=0, le=100)


class ComplianceResult(DomainModel):
    status: ComplianceStatus
    reasons: list[str] = Field(default_factory=list)


class Hook(DomainModel):
    id: UUID = Field(default_factory=uuid4)
    text: str = Field(min_length=3, max_length=280)
    language: Literal["pt-BR"] = "pt-BR"
    library: Library
    pattern_id: str
    mechanisms: list[str]
    objective: Objective
    channel: Channel
    awareness_stage: AwarenessStage = AwarenessStage.PROBLEM_AWARE
    audience: str
    topic: str
    tone: Tone = Tone.PREMIUM
    scores: HookScores
    compliance: ComplianceResult
    explanation: str
    source: Source
    engine_version: Literal[ENGINE_VERSION] = ENGINE_VERSION
    created_at: AwareDatetime = Field(default_factory=lambda: datetime.now(UTC))


class GenerationRequest(DomainModel):
    topic: str = Field(min_length=2, max_length=300)
    channel: Channel
    objective: Objective
    audience: str = Field(min_length=2, max_length=300)
    library: Library = Library.UNIVERSAL
    awareness_stage: AwarenessStage = AwarenessStage.PROBLEM_AWARE
    tone: Tone = Tone.PREMIUM
    intensity: int = Field(default=2, ge=1, le=3)
    mechanism: str | None = None
    context: str | None = Field(default=None, max_length=4000)
    required_words: list[str] = Field(default_factory=list)
    forbidden_words: list[str] = Field(default_factory=list)
    count: int = Field(default=12, ge=1, le=50)
    max_length: int = Field(default=180, ge=30, le=280)
    use_ai: bool = False


class GenerationResponse(DomainModel):
    request_id: UUID
    hooks: list[Hook]
    warnings: list[str] = Field(default_factory=list)
    engine_version: Literal[ENGINE_VERSION] = ENGINE_VERSION
    duration_ms: float = Field(ge=0)


class ContentOSExport(DomainModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    workspace_ref: str
    generated_at: AwareDatetime = Field(default_factory=lambda: datetime.now(UTC))
    hooks: list[Hook]


class HealthResponse(DomainModel):
    status: Literal["ready"] = "ready"
    service: Literal["hook-intelligence"] = "hook-intelligence"
    version: Literal[ENGINE_VERSION] = ENGINE_VERSION
    ai_enabled: bool
