import subprocess

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers.learning import _build_payload
from app.routers.orchestrate import creative_is_published


def test_published_creative_is_immutable() -> None:
    assert creative_is_published({"status": "publicado", "published_at": None})
    assert creative_is_published({"status": "published", "published_at": None})
    assert creative_is_published({"status": "gerado", "published_at": "2026-07-29"})
    assert not creative_is_published({"status": "gerado", "published_at": None})


def test_learning_without_evidence_does_not_invent_medical_thesis() -> None:
    payload = _build_payload([], pending=0, publication_count=0)
    seed = payload["next_sprint_seed"]
    assert seed["thesis"] is None
    assert seed["hook"] is None
    assert seed["reason"] == "Sem evidência suficiente para recomendar tese ou hook."


def test_renders_require_authentication() -> None:
    response = TestClient(app).get("/renders/nonexistent.png")
    assert response.status_code == 401


def test_psql_raises_on_database_failure(monkeypatch) -> None:
    import render_daemon

    monkeypatch.setattr(
        render_daemon.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=args, returncode=2, stdout="", stderr="database failed"
        ),
    )
    with pytest.raises(RuntimeError, match="database failed"):
        render_daemon.psql("select 1")


def test_pending_query_claims_jobs_atomically(monkeypatch) -> None:
    import render_daemon

    captured: list[str] = []

    def fake_psql(sql: str) -> str:
        captured.append(sql)
        return "[]"

    monkeypatch.setattr(render_daemon, "psql", fake_psql)
    assert render_daemon.fetch_pending() == []
    sql = captured[0].lower()
    assert "for update skip locked" in sql
    assert "status='renderizando'" in sql
    assert "returning" in sql
