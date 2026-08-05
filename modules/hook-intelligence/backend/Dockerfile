# syntax=docker/dockerfile:1.7
FROM ghcr.io/astral-sh/uv:0.8.22 AS uv

FROM python:3.11.15-slim-bookworm AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/backend/.venv/bin:${PATH}" \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY --from=uv /uv /uvx /bin/
WORKDIR /app/backend

COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project \
    && useradd --create-home --uid 10001 --shell /usr/sbin/nologin hook \
    && mkdir -p /data \
    && chown hook:hook /data

COPY --chown=hook:hook backend/hook_intelligence ./hook_intelligence
COPY --chown=hook:hook contracts /app/contracts
COPY --chown=hook:hook data /app/data

USER hook
EXPOSE 8000

CMD ["python", "-c", "import os; import uvicorn; from hook_intelligence.api.main import create_app; uvicorn.run(create_app(database_url=os.environ.get('HOOK_DATABASE_URL', 'sqlite:////data/hooks.db')), host='0.0.0.0', port=8000)"]
