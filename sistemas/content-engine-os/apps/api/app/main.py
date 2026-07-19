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
from app.routers.stories_broll import router as stories_broll_router
from app.routers.bi import router as bi_router
from app.routers.social_selling import router as social_selling_router
from app.routers.weekly_command import router as weekly_command_router
from app.routers.learning import router as learning_router
from app.routers.external_learning import router as external_learning_router
from app.routers.compliance import router as compliance_router
from app.routers.dra_media import router as dra_media_router
from app.routers.ads import router as ads_router
from app.routers.publishing import router as publishing_router
from app.routers.motion_videos import router as motion_videos_router

app = FastAPI(title=settings.app_name, version="0.1.0")

import re as _re
from starlette.concurrency import run_in_threadpool
from starlette.responses import JSONResponse as _JSONResponse
from app.db import get_conn as _get_conn

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.app_base_url,
        "https://conteudo.institutovitalslim.com.br",
        "http://localhost:3010",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Isolamento multi-tenant (defesa central por rota por-ID) ──────────────────
# Rotas por-ID (creatives/{id}/..., assets/{id}/download) NÃO filtravam tenant_id,
# permitindo ler/mutar recurso de outro tenant só com o UUID. Este middleware exige
# que o recurso pertença ao tenant resolvido (tenant_slug -> default 'demo'); caso
# contrário 404, ANTES da rota rodar. Com 1 tenant (demo) o app atual não muda.
_RX_CREATIVE = _re.compile(r"^/generation/creatives/([0-9a-fA-F-]{36})(?:/|$)")
_RX_ASSET = _re.compile(r"^/assets/([0-9a-fA-F-]{36})/download")


@app.middleware("http")
async def tenant_isolation(request, call_next):
    path = request.url.path
    table = cid = None
    m = _RX_CREATIVE.match(path)
    if m:
        table, cid = "creatives", m.group(1)
    else:
        m = _RX_ASSET.match(path)
        if m:
            table, cid = "content_assets", m.group(1)
    if table and cid:
        slug = request.query_params.get("tenant_slug") or settings.default_tenant_slug

        def _owns() -> bool:
            with _get_conn() as conn, conn.cursor() as cur:
                cur.execute("select id from tenants where slug=%s", (slug,))
                t = cur.fetchone()
                if not t:
                    return False
                if table == "creatives":
                    cur.execute("select 1 from creatives where id=%s and tenant_id=%s", (cid, t["id"]))
                else:
                    cur.execute("select 1 from content_assets where id=%s and tenant_id=%s", (cid, t["id"]))
                return cur.fetchone() is not None

        try:
            ok = await run_in_threadpool(_owns)
        except Exception:
            ok = True  # erro de DB -> fail-open (não derruba uso legítimo; é defesa em profundidade)
        if not ok:
            return _JSONResponse(status_code=404, content={"detail": "recurso não encontrado neste tenant"})
    return await call_next(request)

# ── Gate de autenticação ──────────────────────────────────────────────────────
# Exige sessão válida (cookie cos_session) em todas as rotas, exceto as públicas
# (/health, /, /auth/*, /renders, OPTIONS). SSR repassa o cookie (web/app/api.ts);
# chamadas client-side são same-origin (/api) e mandam o cookie automaticamente.
_AUTH_PUBLIC_EXACT = {"/", "/health", "/docs", "/openapi.json", "/redoc"}


@app.middleware("http")
async def auth_gate(request, call_next):
    path = request.url.path
    if (
        request.method == "OPTIONS"
        or path in _AUTH_PUBLIC_EXACT
        or path.startswith("/auth/")
        or path.startswith("/renders")
    ):
        return await call_next(request)
    from app.auth_core import read_token
    if not read_token(request.cookies.get("cos_session")):
        return _JSONResponse(status_code=401, content={"detail": "não autenticado"})
    return await call_next(request)


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
app.include_router(stories_broll_router)
app.include_router(bi_router)
app.include_router(social_selling_router)
app.include_router(weekly_command_router)
app.include_router(learning_router)
app.include_router(external_learning_router)
app.include_router(compliance_router)
app.include_router(dra_media_router)
app.include_router(ads_router)
app.include_router(publishing_router)
app.include_router(motion_videos_router)

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
            "codex_gateway",
            "workspaces",
            "session_bootstrap",
            "reuse_strategy",
            "supabase_first",
            "quality_review",
            "strategy_intake",
            "assets_library",
            "editorial_calendar",
            "stories_connection_engine",
            "weekly_positioning_sprint",
            "performance_learning_loop",
            "external_reverse_engineering_learning",
            "scientific_compliance_gate",
            "motion_videos_higgsfield_studio",
        ],
    }
