from ivs_pgvector_bench.report import render_html


def test_render_html_contains_decision_metrics_and_comparability_warning_without_secrets():
    payload = {
        "generated_at": "2026-08-02T12:00:00+00:00",
        "comparability_note": "Corpora não equivalentes",
        "decision": {"decision": "KEEP_GBRAIN_NO_STANDALONE_PGVECTOR", "reason": "Sem ganho incremental"},
        "gbrain": {"queries": 6, "passed": 6, "pass_rate": 1.0, "latency_p50_ms": 1200, "latency_p95_ms": 2200, "results": []},
        "pgvector": {"queries": 12, "recall_at_1": 1.0, "recall_at_3": 1.0, "mrr": 1.0, "latency_p50_ms": 5, "latency_p95_ms": 8, "documents": 20, "index_ms": 30, "extension_version": "0.8.6", "results": []},
    }
    html = render_html(payload)

    assert "KEEP_GBRAIN_NO_STANDALONE_PGVECTOR" in html
    assert "100,0%" in html
    assert "Corpora não equivalentes" in html
    assert "postgresql://" not in html
    assert "<html" in html


def test_render_html_names_structured_gbrain_gap_without_recommending_parallel_pilot():
    payload = {
        "generated_at": "2026-08-02T12:00:00+00:00",
        "comparability_note": "Corpora não equivalentes",
        "decision": {
            "decision": "INVESTIGATE_GBRAIN_GAP_NO_STANDALONE_DECISION",
            "reason": "Lacuna estruturada",
        },
        "gbrain": {
            "queries": 6,
            "passed": 5,
            "pass_rate": 5 / 6,
            "latency_p50_ms": 1200,
            "latency_p95_ms": 2200,
            "results": [],
        },
        "pgvector": {
            "queries": 12,
            "recall_at_1": 1.0,
            "recall_at_3": 1.0,
            "mrr": 1.0,
            "latency_p50_ms": 5,
            "latency_p95_ms": 8,
            "documents": 20,
            "index_ms": 30,
            "extension_version": "0.8.6",
            "execution_plan": {"hnsw_used_by_default": False},
            "results": [],
        },
    }
    html = render_html(payload)
    assert "Investigar a lacuna do GBrain sem criar banco paralelo" in html
    assert "Piloto limitado" not in html
    assert "usado pelo plano padrão: não" in html
