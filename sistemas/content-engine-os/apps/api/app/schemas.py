from datetime import datetime
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    app: str
    env: str
    llm_primary: str


class SourceCreate(BaseModel):
    tenant_slug: str = Field(default="demo")
    network: str
    handle_or_url: str
    label: str
    active: bool = True
    finalidade: str | None = None
    objetivo: str | None = None


class ThemeCreate(BaseModel):
    tenant_slug: str = Field(default="demo")
    theme: str
    objective: str
    format_targets: list[str] = Field(default_factory=list)
    notes: str | None = None


class BriefRequest(BaseModel):
    tenant_slug: str = Field(default="demo")
    title: str
    audience: str
    objective: str
    source_type: str = Field(description="manual_theme | source_signal | science_signal")
    notes: str | None = None


class BriefResponse(BaseModel):
    title: str
    thesis: str
    mechanism: str
    objections: list[str]
    hook_ideas: list[str]
    cta: str
    created_at: datetime
