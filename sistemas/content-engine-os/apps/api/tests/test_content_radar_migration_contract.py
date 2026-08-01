from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MIGRATION = ROOT / "db/init/022_content_radar_v1.sql"
HARDENING = ROOT / "db/init/023_content_radar_v1_hardening.sql"
ROLLBACK = ROOT / "docs/content-radar-v1-backend-rollback.md"
RUNNER = ROOT / "scripts/apply_migrations.py"


def test_radar_migration_exists_and_is_additive() -> None:
    sql = MIGRATION.read_text(encoding="utf-8").lower()

    assert "create table if not exists external_radar_sources" in sql
    assert "create table if not exists external_metric_snapshots" in sql
    assert "create table if not exists external_content_baselines" in sql
    assert "create table if not exists external_baseline_members" in sql
    assert "alter table external_content_items add column if not exists" in sql
    assert "drop table external_content_items" not in sql


def test_migration_encodes_closed_source_governance() -> None:
    sql = MIGRATION.read_text(encoding="utf-8").lower()

    for source_kind in ("approved", "candidate", "excluded", "own_account", "thematic_search"):
        assert f"'{source_kind}'" in sql


def test_migration_has_immutable_snapshot_idempotency_key() -> None:
    sql = MIGRATION.read_text(encoding="utf-8").lower()

    assert "collector_run_id" in sql
    assert "metric_basis" in sql
    assert "payload_fingerprint text not null" in sql
    assert "legacy_import" in sql
    assert "unique (tenant_id, content_item_id, metric_basis, provider, collector_run_id)" in sql
    assert "estimated_views" not in sql


def test_baselines_are_versioned_and_explainable() -> None:
    sql = MIGRATION.read_text(encoding="utf-8").lower()

    assert "algorithm_version" in sql
    assert "sample_count" in sql
    assert "median_value" in sql
    assert "baseline_id" in sql
    assert "metric_snapshot_id" in sql
    assert "candidate_metric_snapshot_id" in sql
    assert "observation_window" in sql


def test_migration_is_tenant_specific_and_canonicalizes_legacy_profiles() -> None:
    sql = MIGRATION.read_text(encoding="utf-8").lower()

    assert "where t.slug = 'demo'" in sql
    assert "yuribarbosaoficial" in sql
    assert "oestevaosouza" in sql
    assert "lower(ltrim(btrim(e.source_profile), '@'))" in sql


def test_ideas_state_is_migrated_with_constraints() -> None:
    sql = MIGRATION.read_text(encoding="utf-8").lower()

    assert "create table if not exists ideias_estado" in sql
    assert "estado in ('guardada', 'produzida', 'descartada')" in sql


def test_migration_runner_uses_checksum_ledger_and_advisory_lock() -> None:
    source = RUNNER.read_text(encoding="utf-8").lower()

    assert "schema_migrations" in source
    assert "sha256" in source
    assert "pg_advisory_xact_lock" in source
    assert "--file" in source


def test_post_022_hardening_uses_an_independent_immutable_ingest_ledger() -> None:
    sql = HARDENING.read_text(encoding="utf-8").lower()

    assert "create table if not exists external_ingest_batches" in sql
    assert "create table if not exists external_ingest_ledger" in sql
    assert "unique (tenant_id, provider, collector_run_id)" in sql
    assert "unique (tenant_id, provider, collector_run_id, source_network, external_identity)" in sql
    assert "payload_fingerprint text not null" in sql
    assert "effective_observed_at timestamptz not null" in sql
    assert "immutable" in sql
    ledger_start = sql.index("create table if not exists external_ingest_ledger")
    ledger_end = sql.index(");", ledger_start)
    assert "external_metric_snapshots" not in sql[ledger_start:ledger_end]


def test_hardening_scopes_constraints_and_adds_composite_tenant_fks() -> None:
    sql = HARDENING.read_text(encoding="utf-8").lower()

    assert "conrelid = 'public.ideias_estado'::regclass" in sql
    assert "unique (tenant_id, id)" in sql
    assert "foreign key (tenant_id, radar_source_id)" in sql
    assert "foreign key (tenant_id, content_item_id)" in sql
    assert "foreign key (tenant_id, candidate_metric_snapshot_id)" in sql
    assert "foreign key (tenant_id, baseline_id)" in sql


def test_baseline_uniqueness_includes_candidate_snapshot() -> None:
    sql = HARDENING.read_text(encoding="utf-8").lower()
    router = (ROOT / "apps/api/app/routers/external_learning.py").read_text(encoding="utf-8").lower()

    expected = (
        "unique (tenant_id, candidate_content_item_id, candidate_metric_snapshot_id, "
        "metric_basis, algorithm_version, cutoff_at)"
    )
    assert expected in " ".join(sql.split())
    assert "candidate_metric_snapshot_id, metric_basis, algorithm_version, cutoff_at" in " ".join(router.split())


def test_ideas_state_is_hardened_post_022_and_legacy_rollback_is_documented() -> None:
    sql = HARDENING.read_text(encoding="utf-8").lower()
    rollback = ROLLBACK.read_text(encoding="utf-8").lower()

    assert "ideias_estado_ideia_id_check" in sql
    assert "ideias_estado_estado_check" in sql
    assert "external_content_items_022_state_audit" in sql
    assert "rollback" in rollback
    assert "022" in rollback
