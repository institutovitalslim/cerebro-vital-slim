import csv
import io
import json
from copy import deepcopy
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from jsonschema import ValidationError as JSONSchemaValidationError
from sqlalchemy import text

from hook_intelligence.domain.models import Hook, HookScores
from hook_intelligence.engine.exporter import export_csv, export_json, make_export_payload
from hook_intelligence.storage.database import create_database
from hook_intelligence.storage.repositories import HookRepository


def hook(**overrides):
    values = {
        "id": uuid4(),
        "text": 'Atenção, "saúde":\n=1+1 não é conteúdo',
        "library": "universal",
        "pattern_id": "curiosity-gap",
        "mechanisms": ["open_loop", "contraste"],
        "objective": "curiosity",
        "channel": "reel",
        "audience": "mulheres, 40+",
        "topic": "saúde sustentável",
        "scores": HookScores(
            clarity=90, specificity=80, novelty=75, retention=88, channel_fit=95, overall=86
        ),
        "compliance": {"status": "pass", "reasons": ["seguro"]},
        "explanation": "Explicação com acento.",
        "source": "deterministic",
        "created_at": datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC),
    }
    values.update(overrides)
    return Hook(**values)


def test_plan_roundtrip_favorite_and_valid_json(tmp_path):
    sample_hook = hook()
    before = deepcopy(sample_hook)
    db = create_database(f"sqlite:///{tmp_path}/hooks.db")
    repo = HookRepository(db)
    session_id = repo.save_generation([sample_hook])
    repo.favorite(sample_hook.id)
    payload = repo.export_session(session_id, workspace_ref="ivs-internal")
    assert payload["schema_version"] == "1.0.0"
    assert payload["workspace_ref"] == "ivs-internal"
    assert payload["hooks"][0]["favorite"] is True
    json.dumps(payload)
    assert repo.get_session(session_id) == (sample_hook,)
    assert sample_hook == before


def test_same_hook_two_sessions_global_favorite_and_idempotency():
    repo = HookRepository(create_database("sqlite:///:memory:"))
    item = hook()
    first = repo.save_generation([item])
    second = repo.save_generation([item])
    repo.favorite(str(item.id))
    repo.favorite(item.id)
    assert repo.is_favorite(item.id)
    assert all(repo.export_session(s, "workspace")["hooks"][0]["favorite"] for s in (first, second))
    repo.unfavorite(item.id)
    repo.unfavorite(item.id)
    assert not repo.is_favorite(item.id)
    with pytest.raises(LookupError, match="hook"):
        repo.favorite(uuid4())
    for bad in ("bad-id", "", 1, True):
        with pytest.raises((TypeError, ValueError)):
            repo.is_favorite(bad)


def test_atomic_rejections_and_invalid_inputs():
    repo = HookRepository(create_database("sqlite:///:memory:"))
    good = hook()
    blocked = hook(compliance={"status": "block", "reasons": ["claim"]})
    for items in ([good, blocked], [good, good], [], "not-hooks"):
        with pytest.raises((TypeError, ValueError), match="generation|duplicate|BLOCK|sequence"):
            repo.save_generation(items)
    assert repo.list_sessions()["total"] == 0
    with pytest.raises(LookupError, match="session"):
        repo.get_session(uuid4())
    with pytest.raises(LookupError, match="session"):
        repo.export_session(uuid4(), "workspace")
    for workspace in ("", "  ", 1, True):
        with pytest.raises((TypeError, ValueError)):
            make_export_payload([good], workspace)
    with pytest.raises(ValueError, match="BLOCK"):
        make_export_payload([blocked], "workspace")


def test_pagination_is_stable_and_validated():
    repo = HookRepository(create_database("sqlite:///:memory:"))
    created = [repo.save_generation([hook()]) for _ in range(25)]
    p1 = repo.list_sessions(page=1, page_size=20)
    p2 = repo.list_sessions(page=2, page_size=20)
    assert p1["total"] == 25 and len(p1["items"]) == 20 and len(p2["items"]) == 5
    ids1 = [item["session_id"] for item in p1["items"]]
    ids2 = [item["session_id"] for item in p2["items"]]
    assert not set(ids1) & set(ids2)
    assert ids1 + ids2 == list(reversed(created))
    for kwargs in (
        {"page": 0},
        {"page": True},
        {"page_size": 0},
        {"page_size": 101},
        {"page_size": 1.5},
    ):
        with pytest.raises((TypeError, ValueError)):
            repo.list_sessions(**kwargs)


def test_memory_file_fk_cascade_and_reopen(tmp_path):
    for url in ("sqlite:///:memory:", f"sqlite:///{tmp_path}/file.db"):
        engine = create_database(url)
        repo = HookRepository(engine)
        sid = repo.save_generation([hook()])
        with engine.connect() as connection:
            assert connection.execute(text("PRAGMA foreign_keys")).scalar_one() == 1
        with engine.begin() as connection:
            connection.execute(
                text("DELETE FROM generation_sessions WHERE session_id=:id"), {"id": sid}
            )
            assert (
                connection.execute(
                    text("SELECT count(*) FROM hooks WHERE session_id=:id"), {"id": sid}
                ).scalar_one()
                == 0
            )
    reopened = HookRepository(create_database(f"sqlite:///{tmp_path}/file.db"))
    assert reopened.list_sessions()["total"] == 0
    for invalid in ("postgresql://localhost/db", "sqlite+pysqlite:///:memory:", 1, None):
        with pytest.raises((TypeError, ValueError), match="SQLite|URL"):
            create_database(invalid)
    with pytest.raises(TypeError, match="Engine"):
        HookRepository(object())


def test_exports_validate_and_csv_is_safe_and_deterministic():
    first = hook(text='  =SUM(1,2), "olá"\nlinha')
    second = hook(text="Normal", compliance={"status": "review", "reasons": ["revisar"]})
    payload = make_export_payload([first, second], "ivs-internal", favorites={first.id})
    encoded = export_json(payload)
    assert json.loads(encoded)["hooks"][0]["favorite"] is True
    assert "olá" in encoded
    csv_text = export_csv([first, second], favorites={first.id})
    rows = list(csv.reader(io.StringIO(csv_text)))
    assert rows[0] == [
        "id",
        "text",
        "library",
        "pattern_id",
        "mechanisms",
        "objective",
        "channel",
        "audience",
        "topic",
        "tone",
        "overall_score",
        "compliance_status",
        "compliance_reasons",
        "explanation",
        "source",
        "engine_version",
        "created_at",
        "favorite",
    ]
    assert rows[1][0] == str(first.id) and rows[2][0] == str(second.id)
    assert rows[1][1].startswith("  '\u003d") and rows[1][-1] == "true"
    assert "olá" in csv_text
    invalid = deepcopy(payload)
    invalid["hooks"][0]["favorite"] = "yes"
    with pytest.raises(JSONSchemaValidationError):
        export_json(invalid)
