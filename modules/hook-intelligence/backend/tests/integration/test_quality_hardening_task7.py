import csv
import io
import traceback
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import UTC, datetime
from threading import Event, Thread
from uuid import uuid4

import pytest
from jsonschema import ValidationError as JSONSchemaValidationError
from sqlalchemy import inspect, text
from sqlalchemy.pool import StaticPool

from hook_intelligence.domain.models import Hook, HookScores
from hook_intelligence.engine import exporter
from hook_intelligence.engine.exporter import export_csv, export_json, make_export_payload
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


@pytest.mark.parametrize("url", ["sqlite://", "sqlite:///:memory:"])
def test_memory_static_pool_serializes_complete_repository_transactions(url):
    for _round in range(3):
        engine = create_database(url)
        assert isinstance(engine.pool, StaticPool)
        shared = HookRepository(engine)
        repos = [shared, HookRepository(engine), HookRepository(engine)]
        items = [hook() for _ in range(100)]

        def save(index, repos=repos, items=items):
            repo = repos[index % len(repos)]
            session_id = repo.save_generation([items[index]])
            # Exercise reads and favorite writes while all repositories share one connection.
            assert repo.get_session(session_id) == (items[index],)
            if index % 10 == 0:
                repo.favorite(items[index].id)
                assert repo.is_favorite(items[index].id)
            return session_id

        with ThreadPoolExecutor(max_workers=16) as executor:
            session_ids = list(executor.map(save, range(100)))
        assert shared.list_sessions(page_size=100)["total"] == len(session_ids) == 100
        assert all(shared.get_session(session_id) for session_id in session_ids)
        engine.dispose()


def _select_in_worker(engine):
    completed = Event()
    result = []
    errors = []

    def select_one():
        try:
            with engine.connect() as connection:
                result.append(connection.execute(text("SELECT 1")).scalar_one())
        except Exception as error:  # noqa: BLE001 - surfaced by the worker probe
            errors.append(error)
        finally:
            completed.set()

    worker = Thread(target=select_one, daemon=True)
    worker.start()
    assert completed.wait(timeout=2), "worker checkout remained blocked"
    worker.join(timeout=0)
    assert not errors
    assert result == [1]


@pytest.mark.parametrize("url", ["sqlite://", "sqlite:///:memory:"])
def test_nested_memory_checkouts_leave_no_residual_lock(url):
    engine = create_database(url)
    outer = engine.connect()
    inner = engine.connect()
    inner.close()
    outer.close()

    _select_in_worker(engine)
    engine.dispose()


@pytest.mark.parametrize("url", ["sqlite://", "sqlite:///:memory:"])
def test_nested_memory_checkout_after_rollback_and_invalidation_releases_lock(url):
    engine = create_database(url)
    outer = engine.connect()
    transaction = outer.begin()
    outer.execute(text("SELECT 1"))
    transaction.rollback()
    inner = engine.connect()
    inner.invalidate()
    inner.close()
    outer.close()

    _select_in_worker(engine)
    engine.dispose()


def test_rfc3339_datetime_checker_and_generated_utc_z():
    payload = make_export_payload([hook()], "workspace")
    assert payload["generated_at"].endswith("Z")
    assert payload["hooks"][0]["created_at"].endswith("Z")
    for path in (("generated_at",), ("hooks", 0, "created_at")):
        for invalid in (
            "x",
            "2026-01-02T03:04:05",
            "2026-02-30T03:04:05Z",
            "2026-01-02T03:04:05+12:60",
            "2026-01-02T03:04:05-05:99",
            "2026-01-02T03:04:05+24:00",
        ):
            candidate = deepcopy(payload)
            target = candidate
            for part in path[:-1]:
                target = target[part]
            target[path[-1]] = invalid
            with pytest.raises(JSONSchemaValidationError):
                export_json(candidate)
    for path in (("generated_at",), ("hooks", 0, "created_at")):
        for valid in (
            "2026-01-02T03:04:05Z",
            "2026-01-02T03:04:05+00:00",
            "2026-01-02T03:04:05.123+03:30",
            "2026-01-02T03:04:05-05:45",
        ):
            candidate = deepcopy(payload)
            target = candidate
            for part in path[:-1]:
                target = target[part]
            target[path[-1]] = valid
            export_json(candidate)


def test_validator_reads_both_schemas_once(monkeypatch):
    exporter._validator.cache_clear()
    reads = 0
    original = exporter.Path.read_text

    def spy(path, *args, **kwargs):
        nonlocal reads
        reads += 1
        return original(path, *args, **kwargs)

    monkeypatch.setattr(exporter.Path, "read_text", spy)
    payload = make_export_payload([hook()], "workspace")
    export_json(payload)
    export_json(payload)
    assert reads == 2
    assert exporter._validator.cache_info().hits >= 2
    exporter._validator.cache_clear()


@pytest.mark.parametrize(
    "url",
    [
        "SUPER_SECRET_TOKEN",
        "sqlite:////definitely/missing/SUPER_SECRET_TOKEN/hooks.db?token=SUPER_SECRET_TOKEN",
    ],
)
def test_database_errors_never_expose_url_path_query_or_token(url):
    with pytest.raises((ValueError, RuntimeError)) as caught:
        create_database(url)
    rendered = str(caught.value) + "".join(
        traceback.format_exception(type(caught.value), caught.value, caught.value.__traceback__)
    )
    assert "SUPER_SECRET_TOKEN" not in rendered
    assert url not in rendered
    expected = (
        "failed to initialize SQLite database"
        if url.startswith("sqlite:")
        else "invalid SQLite database URL"
    )
    assert str(caught.value) == expected
    assert caught.value.__cause__ is None
    assert caught.value.__context__ is None

    pending = [caught.value]
    seen = set()
    while pending:
        error = pending.pop()
        if error is None or id(error) in seen:
            continue
        seen.add(id(error))
        assert "SUPER_SECRET_TOKEN" not in str(error)
        assert "SUPER_SECRET_TOKEN" not in repr(error)
        pending.extend((error.__cause__, error.__context__))


@pytest.mark.parametrize(
    "bad", ["\x00", "\ufeff", "\u202e", "\u200b", "\ue000", "\ud800", "\u0378"]
)
def test_csv_rejects_unsafe_unicode_without_echoing_cell(bad):
    item = hook(pattern_id=f"safe{bad}secret")
    with pytest.raises(ValueError, match=r"hooks\[0\]\.pattern_id") as caught:
        export_csv([item])
    assert "secret" not in str(caught.value)


def test_csv_formula_controls_after_legal_whitespace_and_does_not_mutate_hook():
    item = hook(
        text="\t\r\n  =SUM(1,2)",
        audience="\t+cmd",
        topic="\r-1",
        explanation="\n@evil",
    )
    before = deepcopy(item)
    encoded = export_csv([item])
    row = list(csv.reader(io.StringIO(encoded, newline="")))[1]
    assert row[1] == "\t\r\n  '=SUM(1,2)"
    assert row[7] == "\t'+cmd"
    assert row[8] == "\r'-1"
    assert row[13] == "\n'@evil"
    assert item == before
    assert encoded.endswith("\r\n")


def test_export_boundaries_and_recursive_budgets():
    one = hook()
    thousand = [one.model_copy(update={"id": uuid4()}) for _ in range(1000)]
    payload = make_export_payload(thousand, "workspace")
    assert len(payload["hooks"]) == 1000
    with pytest.raises(ValueError, match="1000"):
        make_export_payload(thousand + [hook()], "workspace")

    assert make_export_payload([hook(pattern_id="x" * 4096)], "workspace")
    with pytest.raises(ValueError, match="4096"):
        make_export_payload([hook(pattern_id="x" * 4097)], "workspace")

    candidate = deepcopy(payload)
    candidate["hooks"][0]["mechanisms"] = ["x"] * 65
    with pytest.raises(ValueError, match="64"):
        export_json(candidate)

    huge = deepcopy(payload)
    huge["hooks"][0]["pattern_id"] = "x" * 5_000_000
    with pytest.raises(ValueError, match="4096"):
        export_json(huge)

    cyclic = deepcopy(payload)
    cyclic["hooks"][0]["cycle"] = cyclic
    with pytest.raises(ValueError, match="cycle"):
        export_json(cyclic)


def test_total_text_budget_is_enforced_before_schema_validation():
    payload = make_export_payload([hook()], "workspace")
    payload["padding"] = ["x" * 4096 for _ in range(64)]
    # Nest legal-sized collections until the aggregate text budget is exceeded.
    payload["padding"] = [deepcopy(payload["padding"]) for _ in range(8)]
    with pytest.raises(ValueError, match="2000000"):
        export_json(payload)


def test_hooks_hook_id_index_is_used_for_favorite_lookup():
    engine = create_database("sqlite:///:memory:")
    names = {index["name"] for index in inspect(engine).get_indexes("hooks")}
    assert "ix_hooks_hook_id" in names
    with engine.connect() as connection:
        plan = connection.execute(
            text("EXPLAIN QUERY PLAN SELECT row_id FROM hooks WHERE hook_id = :id LIMIT 1"),
            {"id": str(uuid4())},
        ).all()
    assert any("ix_hooks_hook_id" in str(row) for row in plan)
    engine.dispose()
