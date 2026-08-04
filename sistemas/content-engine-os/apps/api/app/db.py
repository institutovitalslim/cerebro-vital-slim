from __future__ import annotations

from contextlib import contextmanager
import psycopg
from psycopg.rows import dict_row

from app.config import settings

# Pool de conexões (psycopg_pool). Reusa conexões em vez de abrir uma por request
# (sob carga, evitava ~14 conexões novas a c=50). Fallback p/ conexão-por-request se
# o pacote/abertura do pool falhar — assim a API NUNCA deixa de subir por causa disto.
_pool = None
try:
    from psycopg_pool import ConnectionPool

    _pool = ConnectionPool(
        settings.database_url,
        min_size=2,
        max_size=10,
        max_idle=60,
        kwargs={"row_factory": dict_row},
        open=True,
    )
except Exception:
    _pool = None


@contextmanager
def get_conn():
    if _pool is not None:
        with _pool.connection() as conn:
            yield conn
            conn.commit()
    else:
        conn = psycopg.connect(settings.database_url, row_factory=dict_row)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()
