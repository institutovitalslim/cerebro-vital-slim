from fastapi import APIRouter
from app.config import settings

router = APIRouter(prefix="/platform", tags=["platform"])


@router.get("/stack")
def stack_status() -> dict:
    return {
        "runtime": "vps-first",
        "auth_provider": "supabase" if settings.supabase_url else "bootstrap-local",
        "database_provider": "supabase-postgres" if settings.supabase_url else "local-postgres",
        "storage_provider": "supabase-storage" if settings.supabase_url else "local-storage-pending",
        "llm_primary": settings.llm_primary,
        "llm_fallback": "n/a (codex-only)",
        "llm_live": bool(settings.codex_gateway_url),
        "supabase": {
            "configured": bool(settings.supabase_url and settings.supabase_anon_key),
            "project_url_present": bool(settings.supabase_url),
            "anon_key_present": bool(settings.supabase_anon_key),
            "service_role_present": bool(settings.supabase_service_role_key),
        },
    }
