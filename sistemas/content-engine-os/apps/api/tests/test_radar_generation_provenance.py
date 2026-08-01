from __future__ import annotations

import json
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers import orchestrate, stories


PROVENANCE = {
    "source": "radar",
    "radar_item_id": "11111111-1111-4111-8111-111111111111",
    "radar_external_id": "ABC_123",
    "radar_baseline_id": "33333333-3333-4333-8333-333333333333",
    "radar_snapshot_id": "22222222-2222-4222-8222-222222222222",
    "radar_cutoff_at": "2026-07-29T12:00:00+00:00",
    "radar_algorithm_version": "content-radar-v1.0",
}


class FakeCursor:
    def __init__(self, db: "FakeDB") -> None:
        self.db = db
        self.row = None

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, sql: str, params=None) -> None:
        params = tuple(params or ())
        # Detecta regressão de contrato SQL antes de um teste de integração real.
        assert sql.count("%s") == len(params), (sql, params)
        normalized = " ".join(sql.split()).lower()
        self.db.executions.append((normalized, params))
        if "select id from tenants" in normalized:
            self.row = {"id": self.db.tenant_id}
        elif "from external_content_items e" in normalized and "external_metric_snapshots" in normalized:
            self.db.validated_tenant = params[3]
            self.row = {"?column?": 1} if self.db.radar_chain_exists else None
        elif "insert into creative_test_cycles" in normalized:
            self.db.cycle_insert = params
            self.row = {"id": "cycle-1", "created_at": datetime.now(timezone.utc)}
        elif "insert into creatives" in normalized:
            self.db.creative_insert = params
            self.row = {"id": "creative-1", "created_at": datetime.now(timezone.utc)}
        elif "insert into story_sequences" in normalized:
            self.db.story_insert = params
            self.row = {"id": "story-1", "created_at": datetime.now(timezone.utc)}
        else:
            self.row = None

    def fetchone(self):
        return self.row

    def fetchall(self):
        return []


class FakeConnection:
    def __init__(self, db: "FakeDB") -> None:
        self.db = db

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def cursor(self):
        return FakeCursor(self.db)


class FakeDB:
    tenant_id = "tenant-a"

    def __init__(self, *, radar_chain_exists: bool = True) -> None:
        self.radar_chain_exists = radar_chain_exists
        self.validated_tenant = None
        self.executions: list[tuple[str, tuple]] = []
        self.creative_insert = None
        self.cycle_insert = None
        self.story_insert = None

    @contextmanager
    def connect(self):
        yield FakeConnection(self)


def _client(router) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.fixture
def fake_generation(monkeypatch):
    db = FakeDB()
    monkeypatch.setattr(orchestrate, "get_conn", db.connect)
    monkeypatch.setattr(orchestrate, "_fetch_context", lambda *_args: (None, [], {}))
    monkeypatch.setattr(orchestrate, "_recent_titles", lambda *_args: [])

    async def fake_motor(*_args, **_kwargs):
        return {
            "content": json.dumps({
                "title": "Tese Radar",
                "hook": "Hook Radar",
                "caption": "Legenda",
                "hashtags": ["#ivs"],
                "description": "Descrição auditável suficientemente longa para o gate.",
            }),
            "model": "test",
            "mode": "contract",
        }

    monkeypatch.setattr(orchestrate, "_motor", fake_motor)
    return db


def test_orchestrate_post_validates_tenant_and_persists_provenance_in_brief_and_column(fake_generation) -> None:
    response = _client(orchestrate.router).post(
        "/generation/orchestrate",
        json={
            **PROVENANCE,
            "tenant_slug": "demo",
            "formato": "estatico",
            "objetivo": "desejo",
            "tema": "Tese adaptada",
            "thesis": "Tese original",
            "hook": "Hook original",
            "source_objective": "prova_e_metodo",
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["provenance"]["radar_item_id"] == PROVENANCE["radar_item_id"]
    assert fake_generation.validated_tenant == fake_generation.tenant_id
    assert fake_generation.creative_insert is not None
    brief = json.loads(fake_generation.creative_insert[11])
    stored = json.loads(fake_generation.creative_insert[-1])
    assert brief["provenance"] == stored
    assert brief["radar_snapshot_id"] == PROVENANCE["radar_snapshot_id"]
    assert brief["thesis"] == "Tese original"
    assert brief["hook"] == "Hook original"
    assert brief["source_objective"] == "prova_e_metodo"


def test_matrix_post_persists_same_provenance_on_cycle_and_every_variant(fake_generation) -> None:
    response = _client(orchestrate.router).post(
        "/generation/matrix",
        json={
            **PROVENANCE,
            "tenant_slug": "demo",
            "formato": "estatico",
            "tema": "Matriz Radar",
            "angulos": ["metodo"],
            "hooks": ["mecanismo"],
            "objecoes": ["ja_tentei_de_tudo"],
            "ctas": ["pre_avaliacao"],
            "visuais": ["texto_premium"],
            "visual_hook_mechanics": ["text_slide_in"],
            "thesis": "Tese matriz",
            "hook": "Hook matriz",
            "source_objective": "prova_e_metodo",
        },
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["created"] == 1
    assert body["errors"] == []
    assert json.loads(fake_generation.cycle_insert[-1]) == body["provenance"]
    assert json.loads(fake_generation.creative_insert[-1]) == body["provenance"]


def test_stories_post_preserves_source_context_and_provenance(monkeypatch) -> None:
    db = FakeDB()
    monkeypatch.setattr(stories, "get_conn", db.connect)
    response = _client(stories.router).post(
        "/stories/sequences",
        json={
            **PROVENANCE,
            "tenant_slug": "demo",
            "title": "Tese Radar",
            "sequence_type": "sem_culpa",
            "objective": "prova",
            "source_objective": "prova_e_metodo",
            "main_objection": "culpa",
            "thesis": "Tese Radar original",
            "hook": "Hook Radar original",
            "payload": {},
        },
    )

    assert response.status_code == 200, response.text
    stored_payload = json.loads(db.story_insert[8])
    stored_provenance = json.loads(db.story_insert[-1])
    assert stored_payload["source_context"] == {
        "source": "radar",
        "thesis": "Tese Radar original",
        "hook": "Hook Radar original",
        "objective": "prova_e_metodo",
        "effective_objective": "prova",
    }
    assert stored_payload["provenance"] == stored_provenance
    assert response.json()["provenance"] == stored_provenance


@pytest.mark.parametrize(
    "override",
    [
        {"radar_item_id": "not-a-uuid"},
        {"radar_external_id": "ftp://perfil inválido"},
        {"radar_algorithm_version": "versão com espaços"},
        {"radar_cutoff_at": "2026-07-29T12:00:00"},
        {"radar_snapshot_id": None},
    ],
)
def test_receiver_rejects_malformed_or_partial_radar_handoff(override) -> None:
    response = _client(stories.router).post(
        "/stories/sequences",
        json={
            **PROVENANCE,
            **override,
            "title": "Radar",
            "sequence_type": "sem_culpa",
            "objective": "prova",
            "main_objection": "culpa",
        },
    )
    assert response.status_code == 422


def test_cross_tenant_or_inconsistent_radar_chain_is_rejected(monkeypatch) -> None:
    db = FakeDB(radar_chain_exists=False)
    monkeypatch.setattr(stories, "get_conn", db.connect)
    response = _client(stories.router).post(
        "/stories/sequences",
        json={
            **PROVENANCE,
            "title": "Radar",
            "sequence_type": "sem_culpa",
            "objective": "prova",
            "main_objection": "culpa",
        },
    )
    assert response.status_code == 422
    assert db.story_insert is None


def test_migration_is_additive_idempotent_and_covers_piece_matrix_and_stories() -> None:
    root = Path(__file__).resolve().parents[3]
    sql = (root / "db/init/024_radar_creative_provenance.sql").read_text(encoding="utf-8").lower()
    for table in ("creatives", "creative_test_cycles", "story_sequences"):
        assert f"alter table {table}" in sql
    assert sql.count("add column if not exists radar_provenance") == 3
    assert "drop table" not in sql
    for field in PROVENANCE:
        if field != "source":
            assert field in sql
