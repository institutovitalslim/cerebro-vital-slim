from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from time import perf_counter

import psycopg
from psycopg.conninfo import conninfo_to_dict

from .core import HashEmbedding

_EXPECTED_SANDBOX = {
    "host": "127.0.0.1",
    "port": "55432",
    "dbname": "ivs_benchmark",
    "user": "ivs_benchmark",
    "application_name": "ivs_pgvector_benchmark",
}


def _vector_literal(vector: list[float]) -> str:
    return "[" + ",".join(f"{value:.12f}" for value in vector) + "]"


def _validate_sandbox_dsn(dsn: str) -> None:
    try:
        params = conninfo_to_dict(dsn)
    except psycopg.Error as exc:
        raise ValueError("DSN is not the exact ephemeral sandbox") from exc
    allowed_keys = set(_EXPECTED_SANDBOX) | {"password"}
    exact_keys = set(params).issubset(allowed_keys)
    expected = all(str(params.get(key, "")) == value for key, value in _EXPECTED_SANDBOX.items())
    passfile = os.environ.get("PGPASSFILE", "")
    password_available = bool(
        params.get("password")
        or os.environ.get("PGPASSWORD")
        or (passfile and os.path.isfile(passfile))
    )
    if not exact_keys or not expected or not password_available:
        raise ValueError("DSN is not the exact ephemeral sandbox")


@dataclass
class PgvectorBackend:
    dsn: str
    dimensions: int = 384
    embedder: HashEmbedding = field(init=False)

    def __post_init__(self) -> None:
        if type(self.dimensions) is not int:
            raise TypeError("dimensions must be an integer")
        if not 8 <= self.dimensions <= 2000:
            raise ValueError("dimensions must be between 8 and 2000")
        _validate_sandbox_dsn(self.dsn)
        self.embedder = HashEmbedding(self.dimensions)

    def _connect(self):
        params = conninfo_to_dict(self.dsn)
        connection_args = {
            "host": "127.0.0.1",
            "hostaddr": "127.0.0.1",
            "port": 55432,
            "dbname": "ivs_benchmark",
            "user": "ivs_benchmark",
            "application_name": "ivs_pgvector_benchmark",
            "connect_timeout": 5,
            "autocommit": True,
        }
        if params.get("password"):
            connection_args["password"] = params["password"]
        elif os.environ.get("PGPASSWORD"):
            connection_args["password"] = os.environ["PGPASSWORD"]
        else:
            connection_args["passfile"] = os.environ["PGPASSFILE"]
        conn = psycopg.connect(**connection_args)
        conn.execute("SET statement_timeout = 10000")
        return conn

    def reset_and_index(self, docs: list[dict]) -> dict:
        started = perf_counter()
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute("DROP TABLE IF EXISTS ivs_benchmark_documents")
            cur.execute(
                f"""
                CREATE TABLE ivs_benchmark_documents (
                    id text PRIMARY KEY,
                    title text NOT NULL,
                    body text NOT NULL,
                    embedding vector({self.dimensions}) NOT NULL
                )
                """
            )
            for doc in docs:
                text = f"{doc['title']}\n{doc['body']}"
                vector = _vector_literal(self.embedder.embed(text))
                cur.execute(
                    "INSERT INTO ivs_benchmark_documents (id, title, body, embedding) VALUES (%s, %s, %s, %s::vector)",
                    (doc["id"], doc["title"], doc["body"], vector),
                )
            cur.execute(
                "CREATE INDEX ivs_benchmark_embedding_hnsw ON ivs_benchmark_documents USING hnsw (embedding vector_cosine_ops)"
            )
            cur.execute("ANALYZE ivs_benchmark_documents")
        return {"documents": len(docs), "index_ms": round((perf_counter() - started) * 1000, 3)}

    def search(self, query: str, limit: int = 3) -> list[dict]:
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")
        vector = _vector_literal(self.embedder.embed(query))
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, title, 1 - (embedding <=> %s::vector) AS score
                FROM ivs_benchmark_documents
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (vector, vector, limit),
            )
            return [
                {"id": row[0], "title": row[1], "score": float(row[2])}
                for row in cur.fetchall()
            ]

    def index_plan(self, query: str, limit: int = 3) -> dict:
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")
        vector = _vector_literal(self.embedder.embed(query))
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                EXPLAIN (FORMAT JSON)
                SELECT id FROM ivs_benchmark_documents
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (vector, limit),
            )
            plan = cur.fetchone()[0]
            cur.execute(
                "SELECT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'ivs_benchmark_embedding_hnsw')"
            )
            available = bool(cur.fetchone()[0])
        plan_text = json.dumps(plan, ensure_ascii=False)
        return {
            "hnsw_index_available": available,
            "hnsw_used_by_default": "ivs_benchmark_embedding_hnsw" in plan_text,
            "default_plan": plan[0]["Plan"]["Node Type"],
        }

    def count(self) -> int:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM ivs_benchmark_documents")
            return int(cur.fetchone()[0])

    def extension_version(self) -> str:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
            row = cur.fetchone()
            return str(row[0]) if row else ""
