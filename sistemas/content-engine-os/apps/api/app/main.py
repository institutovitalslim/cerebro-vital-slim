from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers.health import router as health_router
from app.routers.briefings import router as briefings_router
from app.routers.sources import router as sources_router
from app.routers.opportunities import router as opportunities_router
from app.routers.generation import router as generation_router
from app.routers.workspaces import router as workspaces_router
from app.routers.auth import router as auth_router
from app.routers.strategy import router as strategy_router
from app.routers.platform import router as platform_router
from app.routers.quality import router as quality_router
from app.routers.intake import router as intake_router
from app.routers.assets import router as assets_router
from app.routers.calendar import router as calendar_router
from app.routers.orchestrate import router as orchestrate_router
from app.routers.stories import router as stories_router
from app.routers.bi import router as bi_router
from app.routers.social_selling import router as social_selling_router

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(sources_router)
app.include_router(briefings_router)
app.include_router(opportunities_router)
app.include_router(generation_router)
app.include_router(workspaces_router)
app.include_router(auth_router)
app.include_router(strategy_router)
app.include_router(platform_router)
app.include_router(quality_router)
app.include_router(intake_router)
app.include_router(assets_router)
app.include_router(calendar_router)
app.include_router(orchestrate_router)
app.include_router(stories_router)
app.include_router(bi_router)
app.include_router(social_selling_router)

os.makedirs("/root/cerebro-vital-slim/sistemas/content-engine-os/storage/assets/renders", exist_ok=True)
app.mount("/renders", StaticFiles(directory="/root/cerebro-vital-slim/sistemas/content-engine-os/storage/assets/renders"), name="renders")


@app.get("/")
def root() -> dict:
    return {
        "app": settings.app_name,
        "env": settings.app_env,
        "status": "bootstrapped",
        "modules": [
            "auth",
            "sources",
            "manual_themes",
            "opportunities",
            "briefings",
            "creative_generation",
            "openrouter_gateway",
            "workspaces",
            "session_bootstrap",
            "reuse_strategy",
            "supabase_first",
            "quality_review",
            "strategy_intake",
            "assets_library",
            "editorial_calendar",
            "stories_connection_engine",
        ],
    }
