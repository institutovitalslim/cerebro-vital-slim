import csv
import io
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import UTC, datetime, timedelta, timezone
from uuid import uuid4

import pytest
from jsonschema import ValidationError as JSONSchemaValidationError
from sqlalchemy import event, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool

from hook_intelligence.domain.models import Hook, HookScores
from hook_intelligence.engine.exporter import export_csv, export_json, make_export_payload
from hook_intelligence.storage import database as database_module
from hook_intelligence.storage.database import create_database
from hook_intelligence.storage.repositories import HookRepository


def hook(**overrides):
    values = {
        "id": uuid4(),
        "text": "Uma abertura válida para o conteúdo",
        "library": "universal",
        "pattern_id": "curiosity-gap",
        "mechanisms": ["open_loop"],
        "objective": "curiosity",
        "channel": "reel",
        "audience": "adultos",
        "topic": "saúde",
        "scores": HookScores(
            clarity=90, specificity=80, novelty=75, retention=88, channel_fit=95, overall=86
        ),
        "compliance": {"status": "pass", "reasons": []},
        "explanation": "Explicação",
        "source": "deterministic",
        "created_at": datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC),
    }
    values.update(overrides)
    return Hook(**values)


@pytest.mark.parametrize(
    "url",
    [
        "sqlite://",
        "sqlite:///:memory:",
        "sqlite:///:memory:?timeout=5",
        "sqlite+pysqlite:///:memory:",
        "sqlite+pysqlite:///:memory:?timeout=5",
        "sqlite:///file:memdb1?mode=memory&cache=shared&uri=true",
    ],
)
def test_all_sqlite_memory_urls_use_static_pool_fk_and_do_not_create_uri_file(
    url, tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    engine = create_database(url)
    assert isinstance(engine.pool, StaticPool)
    with engine.connect() as connection:
        assert connection.execute(text("PRAGMA foreign_keys")).scalar_one() == 1
    assert not (tmp_path / "file:memdb1").exists()
    engine.dispose()


def test_explicit_sqlite_file_driver_uses_regular_pool_and_initialization_is_contextual(tmp_path):
    engine = create_database(f"sqlite+pysqlite:///{tmp_path}/hooks.db")
    assert not isinstance(engine.pool, StaticPool)
    with engine.connect() as connection:
        assert connection.execute(text("PRAGMA foreign_keys")).scalar_one() == 1
    engine.dispose()

    missing = tmp_path / "missing" / "hooks.db"
    with pytest.raises(RuntimeError, match="failed to initialize SQLite database"):
        create_database(f"sqlite:///{missing}")
    assert not missing.exists()

    with pytest.raises(ValueError, match="only SQLite"):
        create_database("postgresql://localhost/hooks")


def test_failed_schema_initialization_disposes_created_engine(monkeypatch):
    disposed = []
    original_dispose = Engine.dispose

    def track_dispose(engine):
        disposed.append(engine)
        original_dispose(engine)

    def fail_create_all(_engine):
        raise OSError("forced schema failure")

    monkeypatch.setattr(Engine, "dispose", track_dispose)
    monkeypatch.setattr(database_module.metadata, "create_all", fail_create_all)
    with pytest.raises(RuntimeError, match="failed to initialize SQLite database"):
        create_database("sqlite:///:memory:")
    assert len(disposed) == 1


def test_json_export_normalizes_each_timestamp_to_utc_without_mutation():
    plus_three = hook(created_at=datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone(timedelta(hours=3))))
    minus_five = hook(
        created_at=datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone(timedelta(hours=-5)))
    )
    before = deepcopy((plus_three, minus_five))
    payload = make_export_payload(
        [plus_three, minus_five],
        "ivs-internal",
        generated_at=datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone(timedelta(hours=3))),
    )
    assert payload["generated_at"] == "2026-01-02T00:04:05Z"
    assert [item["created_at"] for item in payload["hooks"]] == [
        "2026-01-02T00:04:05Z",
        "2026-01-02T08:04:05Z",
    ]
    assert (plus_three, minus_five) == before


@pytest.mark.parametrize("column", ["scores", "compliance"])
def test_malformed_persisted_json_is_contextualized_by_session(column):
    engine = create_database("sqlite:///:memory:")
    repo = HookRepository(engine)
    session_id = repo.save_generation([hook()])
    with engine.begin() as connection:
        connection.execute(
            text(f"UPDATE hooks SET {column} = '{{' WHERE session_id = :session_id"),
            {"session_id": session_id},
        )
    with pytest.raises(
        ValueError, match=rf"invalid persisted Hook payload in session {session_id}"
    ):
        repo.get_session(session_id)


@pytest.mark.parametrize(
    ("column", "value"),
    [("channel", "invalid-channel"), ("created_at", "not-a-timestamp")],
)
def test_decoded_invalid_persisted_values_keep_hook_context(column, value):
    engine = create_database("sqlite:///:memory:")
    repo = HookRepository(engine)
    item = hook()
    session_id = repo.save_generation([item])
    with engine.begin() as connection:
        connection.execute(
            text(f"UPDATE hooks SET {column} = :value WHERE session_id = :session_id"),
            {"value": value, "session_id": session_id},
        )
    with pytest.raises(ValueError, match=rf"invalid persisted Hook payload for hook {item.id}"):
        repo.get_session(session_id)


@pytest.mark.parametrize(
    "invalid",
    [
        " leading",
        "trailing ",
        "",
        "---",
        "a\x00b",
        "a\u202eb",
        "a\u200bb",
        "a\ue000b",
        "a" * 257,
    ],
)
def test_workspace_ref_rejects_unsafe_values_with_context(invalid):
    with pytest.raises((TypeError, ValueError), match="workspace_ref"):
        make_export_payload([hook()], invalid)


def test_workspace_ref_is_nfkc_normalized_and_input_is_unchanged():
    workspace = "ＩＶＳ-internal"
    payload = make_export_payload([hook()], workspace)
    assert payload["workspace_ref"] == "IVS-internal"
    assert workspace == "ＩＶＳ-internal"


def test_orphan_favorite_is_idempotent_until_unfavorited():
    engine = create_database("sqlite:///:memory:")
    repo = HookRepository(engine)
    item = hook()
    session_id = repo.save_generation([item])
    repo.favorite(item.id)
    with engine.begin() as connection:
        connection.execute(
            text("DELETE FROM generation_sessions WHERE session_id=:session_id"),
            {"session_id": session_id},
        )
    assert repo.is_favorite(item.id)
    repo.favorite(item.id)
    assert repo.is_favorite(item.id)
    repo.unfavorite(item.id)
    assert not repo.is_favorite(item.id)
    with pytest.raises(LookupError, match="does not exist"):
        repo.favorite(item.id)


def test_favorite_ids_are_strict_and_canonicalized():
    item = hook()
    uppercase = str(item.id).upper()
    assert make_export_payload([item], "workspace", favorites=[uppercase])["hooks"][0]["favorite"]
    assert list(csv.reader(io.StringIO(export_csv([item], favorites=[uppercase]))))[1][-1] == "true"
    for invalid in ([True], [1], [" bad"], ["bad"], [object()]):
        with pytest.raises((TypeError, ValueError), match=r"favorites\[0\]"):
            make_export_payload([item], "workspace", favorites=invalid)
    with pytest.raises(TypeError, match="collection"):
        make_export_payload([item], "workspace", favorites=(value for value in [item.id]))


def test_csv_is_rfc4180_crlf_and_roundtrips_special_cells():
    item = hook(
        text='  =SUM(1,2), "quoted"\r\nsecond line',
        audience="a,b",
        topic="line one\nline two",
        explanation='say "hello"',
    )
    exported = export_csv([item])
    assert exported.endswith("\r\n")
    assert "\r\n" in exported
    rows = list(csv.reader(io.StringIO(exported, newline="")))
    assert len(rows) == 2
    assert rows[1][1] == '  \'=SUM(1,2), "quoted"\r\nsecond line'
    assert rows[1][7] == "a,b"
    assert rows[1][8] == "line one\nline two"
    assert rows[1][13] == 'say "hello"'


def test_favorite_concurrency_and_contract_backward_compatibility(tmp_path):
    engine = create_database(f"sqlite:///{tmp_path}/concurrent.db")
    repo = HookRepository(engine)
    item = hook()
    repo.save_generation([item])
    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(lambda _: repo.favorite(item.id), range(24)))
    assert repo.is_favorite(item.id)

    payload = make_export_payload([item], "ivs-internal")
    old_hook_payload = deepcopy(payload)
    old_hook_payload["hooks"][0].pop("favorite")
    export_json(old_hook_payload)
    invalid = deepcopy(payload)
    invalid["hooks"][0]["favorite"] = "false"
    with pytest.raises(JSONSchemaValidationError):
        export_json(invalid)
    engine.dispose()


def test_save_generation_rolls_back_session_when_second_row_insert_fails():
    engine = create_database("sqlite:///:memory:")
    repo = HookRepository(engine)
    inserts = 0

    def fail_second_hook_insert(_conn, _cursor, statement, _parameters, _context, _many):
        nonlocal inserts
        if statement.startswith("INSERT INTO hooks"):
            inserts += 1
            if inserts == 2:
                raise RuntimeError("forced second-row failure")

    event.listen(engine, "before_cursor_execute", fail_second_hook_insert)
    with pytest.raises(RuntimeError, match="forced second-row failure"):
        repo.save_generation([hook(), hook()])
    event.remove(engine, "before_cursor_execute", fail_second_hook_insert)
    assert repo.list_sessions()["total"] == 0
    engine.dispose()
