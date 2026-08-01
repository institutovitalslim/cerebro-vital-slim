#!/usr/bin/env python3
"""Aplica migrations SQL explícitas com ledger, checksum e advisory lock.

Uso:
  DATABASE_URL=... python3 scripts/apply_migrations.py --file db/init/022_content_radar_v1.sql

O runner não percorre automaticamente migrations antigas para evitar reexecutar
seeds em bancos existentes. Cada rollout informa explicitamente os arquivos.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import sys

import psycopg
from psycopg.rows import dict_row


LEDGER_SQL = """
create table if not exists schema_migrations (
  version text primary key,
  checksum_sha256 text not null,
  applied_at timestamptz not null default now()
)
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Content Engine OS migration runner")
    parser.add_argument(
        "--file",
        dest="files",
        action="append",
        required=True,
        help="Arquivo SQL a aplicar. Pode ser repetido.",
    )
    return parser.parse_args()


def apply_file(conn: psycopg.Connection, path: Path) -> dict[str, str]:
    if not path.is_file():
        raise FileNotFoundError(path)

    sql = path.read_text(encoding="utf-8")
    checksum = sha256(sql.encode("utf-8")).hexdigest()
    version = path.name

    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("select pg_advisory_xact_lock(hashtext(%s))", ("content-engine-os-schema-migrations",))
        cur.execute(LEDGER_SQL)
        cur.execute(
            "select checksum_sha256 from schema_migrations where version=%s",
            (version,),
        )
        existing = cur.fetchone()
        if existing:
            if existing["checksum_sha256"] != checksum:
                raise RuntimeError(
                    f"migration {version} já aplicada com checksum diferente; crie uma nova migration"
                )
            return {"version": version, "status": "already_applied", "sha256": checksum}

        cur.execute(sql, prepare=False)
        cur.execute(
            "insert into schema_migrations(version, checksum_sha256) values (%s, %s)",
            (version, checksum),
        )
    return {"version": version, "status": "applied", "sha256": checksum}


def main() -> int:
    args = parse_args()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL não definido", file=sys.stderr)
        return 2

    results: list[dict[str, str]] = []
    with psycopg.connect(database_url) as conn:
        for raw_path in args.files:
            result = apply_file(conn, Path(raw_path).resolve())
            conn.commit()
            results.append(result)

    print(json.dumps({"status": "ok", "migrations": results}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
