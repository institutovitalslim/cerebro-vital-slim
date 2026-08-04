from fastapi import FastAPI

from hook_intelligence import ENGINE_VERSION
from hook_intelligence.domain.models import HealthResponse

app = FastAPI(title="Hook Intelligence Engine", version=ENGINE_VERSION)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(ai_enabled=False)
