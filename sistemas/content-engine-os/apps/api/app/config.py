from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Content Engine OS API"
    app_env: str = "development"
    app_base_url: str = "http://localhost:3010"
    database_url: str = "postgresql://content_engine:content_engine_dev@localhost:5434/content_engine"
    redis_url: str = "redis://localhost:6381/0"
    default_tenant_slug: str = "demo"
    content_os_secret: str | None = None
    llm_primary: str = "codex/gpt-5.5-oauth"  # motor real (rótulo p/ /health e /platform)
    codex_gateway_url: str | None = None
    codex_gateway_token: str | None = None
    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    supabase_service_role_key: str | None = None
    content_radar_v1_enabled: bool = False

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')


settings = Settings()
