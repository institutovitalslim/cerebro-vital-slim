from ivs_pgvector_bench.core import (
    HashEmbedding,
    compute_metrics,
    decide,
    evaluate_gates,
)

GATE_CONFIG = {
    "pgvector_recall_at_3_min": 0.90,
    "pgvector_mrr_min": 0.80,
    "pgvector_p95_ms_max": 250,
    "gbrain_pass_rate_min": 0.90,
    "gbrain_expected_path_max_rank": 3,
}


def _gates(gbrain, pgvector):
    return evaluate_gates(gbrain=gbrain, pgvector=pgvector, thresholds=GATE_CONFIG)


def test_hash_embedding_is_deterministic_normalized_and_semantically_sensitive():
    embedder = HashEmbedding(dimensions=256)
    first = embedder.embed("confirmação de agenda da Clara")
    second = embedder.embed("confirmação de agenda da Clara")
    unrelated = embedder.embed("infraestrutura de vídeo e renderização")
    assert first == second
    assert abs(sum(value * value for value in first) - 1.0) < 1e-9
    assert sum(a * b for a, b in zip(first, unrelated)) < 0.7


def test_compute_metrics_calculates_recall_mrr_and_latency_percentiles():
    rows = [
        {"expected": "doc-a", "retrieved": ["doc-a", "doc-b"], "latency_ms": 10.0},
        {"expected": "doc-c", "retrieved": ["doc-x", "doc-c"], "latency_ms": 20.0},
        {"expected": "doc-z", "retrieved": ["doc-x", "doc-y"], "latency_ms": 30.0},
    ]
    metrics = compute_metrics(rows)
    assert metrics["recall_at_1"] == 1 / 3
    assert metrics["recall_at_3"] == 2 / 3
    assert metrics["mrr"] == 0.5
    assert metrics["latency_p50_ms"] == 20.0
    assert metrics["latency_p95_ms"] == 30.0


def test_evaluate_gates_consumes_manifest_thresholds_and_persists_each_result():
    gbrain = {"pass_rate": 0.83}
    pgvector = {"recall_at_3": 0.7, "mrr": 0.6, "latency_p95_ms": 300.0}
    gates = _gates(gbrain, pgvector)
    by_name = {gate["name"]: gate for gate in gates}
    assert by_name["gbrain_pass_rate"]["passed"] is False
    assert by_name["pgvector_recall_at_3"]["threshold"] == 0.90
    assert by_name["pgvector_recall_at_3"]["passed"] is False
    assert by_name["pgvector_mrr"]["passed"] is False
    assert by_name["pgvector_latency_p95_ms"]["passed"] is False
    assert all({"observed", "threshold", "comparator", "scope", "passed"} <= gate.keys() for gate in gates)


def test_decision_rejects_duplicate_layer_when_gbrain_is_healthy_and_candidate_passes_synthetic_gates():
    gbrain = {"pass_rate": 1.0, "latency_p95_ms": 300.0}
    pgvector = {"recall_at_3": 1.0, "mrr": 1.0, "latency_p95_ms": 30.0}
    result = decide(gbrain=gbrain, pgvector=pgvector, gates=_gates(gbrain, pgvector))
    assert result["decision"] == "KEEP_GBRAIN_NO_STANDALONE_PGVECTOR"
    assert result["candidate_gate_status"] == "PASS_SYNTHETIC_ONLY"


def test_decision_records_candidate_gate_failure_instead_of_treating_it_as_success():
    gbrain = {"pass_rate": 1.0, "latency_p95_ms": 300.0}
    pgvector = {"recall_at_3": 0.1, "mrr": 0.1, "latency_p95_ms": 999.0}
    result = decide(gbrain=gbrain, pgvector=pgvector, gates=_gates(gbrain, pgvector))
    assert result["decision"] == "KEEP_GBRAIN_NO_STANDALONE_PGVECTOR"
    assert result["candidate_gate_status"] == "FAIL"
    assert "falhou" in result["reason"]


def test_decision_requires_same_corpus_evidence_before_any_pgvector_pilot():
    gbrain = {"pass_rate": 0.6, "latency_p95_ms": 900.0}
    pgvector = {"recall_at_3": 1.0, "mrr": 0.95, "latency_p95_ms": 50.0}
    result = decide(gbrain=gbrain, pgvector=pgvector, gates=_gates(gbrain, pgvector))
    assert result["decision"] == "INVESTIGATE_GBRAIN_GAP_NO_STANDALONE_DECISION"
    assert result["gbrain_gate_status"] == "FAIL"
    assert result["requires_same_corpus_evidence"] is True
