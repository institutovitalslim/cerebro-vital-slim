from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
import time
from pathlib import Path
from urllib.parse import urlsplit

from fastapi.testclient import TestClient
from sqlalchemy import inspect, text

from hook_intelligence.api.main import create_app
from hook_intelligence.storage import HookRepository, create_database

_SECRET = "integration-test-secret"


def _headers(
    tenant: str,
    user: str,
    *,
    method: str = "GET",
    path: str = "/v1/history",
    query: str = "",
    body: bytes = b"",
    timestamp: int | None = None,
    secret: str = _SECRET,
):
    stamp = str(timestamp if timestamp is not None else int(time.time()))
    body_digest = hashlib.sha256(body).hexdigest()
    message = (
        f"{tenant}\n{user}\n{stamp}\n{method.upper()}\n{path}\n{query}\n{body_digest}"
    ).encode()
    signature = hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()
    return {
        "x-content-os-tenant": tenant,
        "x-content-os-user": user,
        "x-content-os-timestamp": stamp,
        "x-content-os-signature": signature,
    }


def _signed_request(
    client: TestClient,
    method: str,
    url: str,
    tenant: str,
    user: str,
    *,
    json_body: dict | None = None,
):
    parsed = urlsplit(url)
    body = (
        json.dumps(json_body, ensure_ascii=False, separators=(",", ":")).encode()
        if json_body is not None
        else b""
    )
    headers = _headers(
        tenant,
        user,
        method=method,
        path=parsed.path,
        query=parsed.query,
        body=body,
    )
    if json_body is not None:
        headers["content-type"] = "application/json"
    return client.request(method, url, content=body or None, headers=headers)


def _payload(topic: str = "sono"):
    return {
        "topic": topic,
        "channel": "reel",
        "objective": "retention",
        "audience": "mulheres acima de 40",
        "library": "universal",
        "count": 1,
    }


def test_signed_context_is_required_and_timestamp_is_fresh(monkeypatch):
    monkeypatch.setenv("HOOK_INTEGRATION_SECRET", _SECRET)
    with TestClient(create_app()) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/v1/history").status_code == 401
        assert (
            client.get(
                "/v1/history",
                headers=_headers("t1", "u1", secret="wrong"),
            ).status_code
            == 401
        )
        stale = int(time.time()) - 301
        assert (
            client.get(
                "/v1/history",
                headers=_headers("t1", "u1", timestamp=stale),
            ).status_code
            == 401
        )
        assert client.get("/v1/history", headers=_headers("t1", "u1")).status_code == 200
        assert (
            client.get(
                "/v1/history",
                headers=_headers("standalone", "u1"),
            ).status_code
            == 401
        )
        assert (
            client.get(
                "/v1/history",
                headers=_headers("t1", "standalone"),
            ).status_code
            == 401
        )


def test_signature_rejects_tampered_method_path_query_and_body(monkeypatch):
    monkeypatch.setenv("HOOK_INTEGRATION_SECRET", _SECRET)
    body = json.dumps(_payload(), separators=(",", ":")).encode()
    valid = _headers(
        "tenant-a",
        "user-a",
        method="POST",
        path="/v1/hooks/generate",
        body=body,
    )
    with TestClient(create_app()) as client:
        valid_with_type = {**valid, "content-type": "application/json"}
        assert (
            client.post(
                "/v1/hooks/generate",
                content=body,
                headers=valid_with_type,
            ).status_code
            == 200
        )
        assert client.get("/v1/hooks/generate", headers=valid).status_code == 401
        assert (
            client.post(
                "/v1/hooks/score",
                content=body,
                headers=valid_with_type,
            ).status_code
            == 401
        )
        assert (
            client.post(
                "/v1/hooks/generate?mode=changed",
                content=body,
                headers=valid_with_type,
            ).status_code
            == 401
        )
        assert (
            client.post(
                "/v1/hooks/generate",
                content=body + b" ",
                headers=valid_with_type,
            ).status_code
            == 401
        )


def test_cross_tenant_and_cross_user_history_hook_favorite_and_export_are_isolated(monkeypatch):
    monkeypatch.setenv("HOOK_INTEGRATION_SECRET", _SECRET)
    with TestClient(create_app()) as client:
        generated_response = _signed_request(
            client,
            "POST",
            "/v1/hooks/generate",
            "tenant-a",
            "user-a",
            json_body=_payload(),
        )
        assert generated_response.status_code == 200, generated_response.text
        generated = generated_response.json()
        session_id = generated["request_id"]
        hook_id = generated["hooks"][0]["id"]

        for tenant, user in (("tenant-b", "user-a"), ("tenant-a", "user-b")):
            assert _signed_request(client, "GET", "/v1/history", tenant, user).json()["total"] == 0
            assert (
                _signed_request(client, "GET", "/v1/favorites", tenant, user).json()["total"] == 0
            )
            assert (
                _signed_request(client, "GET", f"/v1/hooks/{hook_id}", tenant, user).status_code
                == 404
            )
            assert (
                _signed_request(
                    client,
                    "POST",
                    f"/v1/hooks/{hook_id}/favorite",
                    tenant,
                    user,
                ).status_code
                == 404
            )
            assert (
                _signed_request(
                    client,
                    "POST",
                    "/v1/exports/content-os",
                    tenant,
                    user,
                    json_body={"session_id": session_id, "workspace_ref": "workspace"},
                ).status_code
                == 404
            )

        assert (
            _signed_request(client, "GET", f"/v1/hooks/{hook_id}", "tenant-a", "user-a").status_code
            == 200
        )
        assert (
            _signed_request(
                client,
                "POST",
                f"/v1/hooks/{hook_id}/favorite",
                "tenant-a",
                "user-a",
            ).status_code
            == 200
        )
        assert (
            _signed_request(client, "GET", "/v1/favorites", "tenant-a", "user-a").json()["total"]
            == 1
        )
        exported = _signed_request(
            client,
            "POST",
            "/v1/exports/content-os",
            "tenant-a",
            "user-a",
            json_body={"session_id": session_id, "workspace_ref": "workspace"},
        )
        assert exported.json()["hooks"][0]["favorite"] is True


def test_legacy_database_migrates_into_standalone_scope_and_does_not_leak(tmp_path, monkeypatch):
    path = Path(tmp_path) / "legacy.db"
    connection = sqlite3.connect(path)
    connection.executescript(
        """
        CREATE TABLE generation_sessions (
          row_id INTEGER PRIMARY KEY AUTOINCREMENT, session_id VARCHAR(36) NOT NULL UNIQUE,
          created_at VARCHAR(40) NOT NULL);
        CREATE TABLE hooks (
          row_id INTEGER PRIMARY KEY AUTOINCREMENT, session_id VARCHAR(36) NOT NULL,
          position INTEGER NOT NULL, hook_id VARCHAR(36) NOT NULL, text TEXT NOT NULL,
          language VARCHAR(16) NOT NULL, library VARCHAR(32) NOT NULL, pattern_id TEXT NOT NULL,
          mechanisms JSON NOT NULL, objective VARCHAR(32) NOT NULL, channel VARCHAR(32) NOT NULL,
          awareness_stage VARCHAR(32) NOT NULL, audience TEXT NOT NULL, topic TEXT NOT NULL,
          tone VARCHAR(32) NOT NULL, scores JSON NOT NULL, compliance JSON NOT NULL,
          explanation TEXT NOT NULL, source VARCHAR(32) NOT NULL, engine_version VARCHAR(32) NOT NULL,
          created_at VARCHAR(40) NOT NULL,
          UNIQUE(session_id, hook_id), UNIQUE(session_id, position));
        CREATE INDEX ix_hooks_hook_id ON hooks(hook_id);
        CREATE TABLE favorites (hook_id VARCHAR(36) PRIMARY KEY, created_at VARCHAR(40) NOT NULL);
        INSERT INTO generation_sessions (session_id, created_at)
        VALUES ('00000000-0000-0000-0000-000000000001', '2026-01-01T00:00:00Z');
        """
    )
    connection.commit()
    connection.close()

    migrated = create_database(f"sqlite:///{path}")
    backup_path = Path(f"{path}.pre-multitenant.bak")
    assert backup_path.is_file()
    with sqlite3.connect(backup_path) as backup:
        backup_columns = {
            row[1] for row in backup.execute("PRAGMA table_info(generation_sessions)")
        }
        assert "tenant_id" not in backup_columns
        assert "user_id" not in backup_columns
        assert backup.execute("SELECT COUNT(*) FROM generation_sessions").fetchone()[0] == 1

    inspector = inspect(migrated)
    columns = {column["name"] for column in inspector.get_columns("generation_sessions")}
    assert {"tenant_id", "user_id"} <= columns
    assert "ix_hooks_owner_hook_id" in {index["name"] for index in inspector.get_indexes("hooks")}
    assert HookRepository(migrated).list_sessions()["total"] == 1
    with migrated.connect() as db:
        owner = db.execute(text("SELECT tenant_id, user_id FROM generation_sessions")).one()
        assert tuple(owner) == ("standalone", "standalone")

    monkeypatch.setenv("HOOK_INTEGRATION_SECRET", _SECRET)
    with TestClient(create_app(engine=migrated)) as client:
        assert (
            _signed_request(client, "GET", "/v1/history", "tenant-a", "user-a").json()["total"] == 0
        )
    migrated.dispose()
