from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi import HTTPException

from app.content_radar import BaselineObservation, observation_window
from app.routers.external_learning import (
    ExternalIngestRequest,
    _batch_fingerprint,
    _payload_fingerprint,
    _persist_baseline,
    _reserve_ingest_batch,
    effective_new_source_kind,
    require_session_tenant,
    validate_source_transition,
)


ROOT = Path(__file__).resolve().parents[3]
RADAR_PAGE = ROOT / "apps/web/app/radar-externo/page.tsx"
IDEIAS_ROUTER = ROOT / "apps/api/app/routers/ideias.py"
EXTERNAL_ROUTER = ROOT / "apps/api/app/routers/external_learning.py"
PROFILE_COLLECTOR = ROOT / "scripts/instagram_profile_external_collect_ingest.py"


def test_session_tenant_must_match_requested_tenant() -> None:
    assert require_session_tenant({"tid": "tenant-a"}, "tenant-a") == "tenant-a"

    with pytest.raises(HTTPException) as exc:
        require_session_tenant({"tid": "tenant-a"}, "tenant-b")
    assert exc.value.status_code == 404

    with pytest.raises(HTTPException):
        require_session_tenant({}, "tenant-a")


def test_new_profile_source_cannot_self_approve() -> None:
    assert effective_new_source_kind("candidate") == "candidate"
    assert effective_new_source_kind("approved") == "candidate"
    assert effective_new_source_kind("own_account") == "candidate"
    assert effective_new_source_kind("thematic_search") == "thematic_search"


def test_only_owner_can_change_source_governance() -> None:
    with pytest.raises(HTTPException) as exc:
        validate_source_transition("candidate", "approved", actor_role="member")
    assert exc.value.status_code == 403

    validate_source_transition("candidate", "approved", actor_role="owner")


def test_source_governance_keeps_active_flag_in_sync() -> None:
    source = EXTERNAL_ROUTER.read_text(encoding="utf-8")
    assert "active=(%s <> 'excluded')" in source
    assert "returning id::text, source_kind, active" in source


def test_thematic_search_cannot_be_promoted_directly() -> None:
    for target in ("approved", "own_account"):
        with pytest.raises(HTTPException) as exc:
            validate_source_transition("thematic_search", target, actor_role="owner")
        assert exc.value.status_code == 409


def test_observation_age_is_bucketed_for_comparable_baselines() -> None:
    published = datetime(2026, 7, 20, 12, tzinfo=timezone.utc)
    assert observation_window(published, datetime(2026, 7, 21, 11, tzinfo=timezone.utc)) == "0_24h"
    assert observation_window(published, datetime(2026, 7, 22, 12, tzinfo=timezone.utc)) == "24_72h"
    assert observation_window(published, datetime(2026, 7, 25, 12, tzinfo=timezone.utc)) == "72h_7d"
    assert observation_window(published, datetime(2026, 7, 29, 12, tzinfo=timezone.utc)) == "7d_plus"
    assert observation_window(None, datetime(2026, 7, 21, 12, tzinfo=timezone.utc)) is None


def test_feature_flag_has_backend_enforcement_and_legacy_ideas_fallback() -> None:
    source = IDEIAS_ROUTER.read_text(encoding="utf-8")
    assert "settings.content_radar_v1_enabled" in source
    assert 'i["tipo"] != "externo"' in source
    guard = source.index("if settings.content_radar_v1_enabled:")
    external_table = source.index("from external_content_items e")
    assert guard < external_table
    excluded_lookup = source.index("fora = _excluidos(conn, tid)")
    assert source.rfind("if settings.content_radar_v1_enabled:", 0, excluded_lookup) >= 0

    router = EXTERNAL_ROUTER.read_text(encoding="utf-8")
    disabled = router.index("if not settings.content_radar_v1_enabled:", router.index("def overview"))
    schema_check = router.index("_assert_radar_schema(conn)", router.index("def overview"))
    assert disabled < schema_check
    live_actor = router.index("_authenticated_actor(conn, request, tenant_id)", router.index("def overview"))
    assert live_actor < disabled


def test_radar_handoff_uses_supported_source_identifier() -> None:
    source = RADAR_PAGE.read_text(encoding="utf-8")
    assert "source: 'radar'" in source
    assert "source: 'content-radar'" not in source
    assert "post: '/producao/estaticos'" in source
    assert "carousel: '/producao/carrosseis'" in source
    assert "story: '/criar'" in source
    assert "radar_baseline_id" in source
    assert "radar_snapshot_id" in source
    assert "item.maturity === 'target'" in source


def test_missing_publication_time_returns_insufficient_without_database_write() -> None:
    class NoDatabaseWrites:
        def cursor(self):
            raise AssertionError("baseline sem published_at não deve tocar no banco")

    candidate = BaselineObservation(
        content_item_id="candidate",
        external_id="candidate",
        source_network="instagram",
        source_profile="dra.camilapaes",
        canonical_format="reel",
        metric_basis="views",
        metric_value=100,
        observed_at=datetime(2026, 7, 29, 12, tzinfo=timezone.utc),
        published_at=None,
        source_kind="approved",
    )
    result = _persist_baseline(
        NoDatabaseWrites(),
        tenant_id="tenant",
        candidate=candidate,
        candidate_snapshot_id="snapshot",
        observations=[],
        snapshot_ids={},
    )

    assert result["maturity"] == "insufficient"
    assert result["reason"] == "unknown_observation_window"


def test_snapshot_selection_has_total_tie_breakers() -> None:
    source = EXTERNAL_ROUTER.read_text(encoding="utf-8")
    assert "s.created_at desc" in source
    assert "s.provider, s.collector_run_id, s.id desc" in source
    assert "order by observed_at desc, snapshot_id desc" in source
    assert 'actor["role"] != "owner"' in source


def test_server_generated_observation_time_is_not_part_of_batch_identity() -> None:
    payload = ExternalIngestRequest.model_validate(
        {
            "tenant_slug": "demo",
            "provider": "provider-a",
            "collector_run_id": "run-without-time",
            "items": [
                {
                    "source_profile": "perfil",
                    "external_id": "post-1",
                    "metrics": {},
                }
            ],
        }
    )

    assert payload.observed_at is None
    assert _batch_fingerprint(payload) == _batch_fingerprint(payload.model_copy(deep=True))


def test_identical_batch_replay_reuses_effective_time_and_divergence_is_409() -> None:
    class BatchLedger:
        def __init__(self):
            self.rows: dict[tuple[str, str, str], dict] = {}
            self.result = None

        def cursor(self):
            return self

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def execute(self, sql, params):
            key = (str(params[0]), str(params[1]), str(params[2]))
            if "insert into external_ingest_batches" in sql:
                if key in self.rows:
                    self.result = None
                else:
                    self.rows[key] = {
                        "request_fingerprint": params[3],
                        "identity_count": params[4],
                        "effective_observed_at": params[5],
                    }
                    self.result = self.rows[key]
            elif "from external_ingest_batches" in sql:
                self.result = self.rows.get(key)
            else:
                raise AssertionError(sql)

        def fetchone(self):
            return self.result

    payload = ExternalIngestRequest.model_validate(
        {
            "provider": "provider-a",
            "collector_run_id": "run-stable",
            "items": [{"source_profile": "perfil", "external_id": "post-1", "metrics": {}}],
        }
    )
    first_clock = datetime(2026, 7, 29, 12, tzinfo=timezone.utc)
    later_clock = datetime(2026, 7, 30, 18, tzinfo=timezone.utc)
    ledger = BatchLedger()

    first = _reserve_ingest_batch(
        ledger, tenant_id="tenant-a", payload=payload, server_now=first_clock
    )
    replay = _reserve_ingest_batch(
        ledger, tenant_id="tenant-a", payload=payload, server_now=later_clock
    )

    assert first == first_clock
    assert replay == first_clock

    divergent = payload.model_copy(
        update={"items": [payload.items[0].model_copy(update={"caption": "payload divergente"})]}
    )
    with pytest.raises(HTTPException) as exc:
        _reserve_ingest_batch(
            ledger, tenant_id="tenant-a", payload=divergent, server_now=later_clock
        )
    assert exc.value.status_code == 409


def test_items_without_metrics_still_have_a_payload_fingerprint() -> None:
    payload = ExternalIngestRequest.model_validate(
        {
            "provider": "provider-a",
            "collector_run_id": "run-empty-metrics",
            "observed_at": "2026-07-29T12:00:00Z",
            "items": [
                {
                    "source_profile": "perfil",
                    "external_id": "post-1",
                    "metrics": {},
                }
            ],
        }
    )
    item = payload.items[0]

    fingerprint = _payload_fingerprint(
        payload,
        item,
        external_id="post-1",
        actual_profile="perfil",
    )

    assert len(fingerprint) == 64
    assert fingerprint == _payload_fingerprint(
        payload,
        item,
        external_id="post-1",
        actual_profile="perfil",
    )


def test_source_active_is_returned_and_required_for_ideation() -> None:
    source = EXTERNAL_ROUTER.read_text(encoding="utf-8")
    assert '"source_active": bool(source["active"])' in source
    assert 'source["active"]' in source
    assert "rs.active as source_active" in source
    assert 'item.get("source_active")' in source


def test_profile_collector_issues_session_only_for_an_owner() -> None:
    source = PROFILE_COLLECTOR.read_text(encoding="utf-8")
    assert "u.role='owner'" in source
