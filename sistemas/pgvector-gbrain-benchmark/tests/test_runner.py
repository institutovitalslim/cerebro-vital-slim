from ivs_pgvector_bench.runner import assess_gbrain_case, run_gbrain

TRACKED = {
    "cerebro/areas/atendimento/clara-operacao/regra": (
        "cerebro/areas/atendimento/clara-operacao/regra.md"
    )
}


def test_assess_gbrain_case_requires_ranked_tracked_canonical_path():
    case = {
        "name": "Agenda",
        "query": "confirmar agenda",
        "expected_path_prefixes": ["cerebro/areas/atendimento/clara-operacao"],
        "max_rank": 3,
    }
    result = assess_gbrain_case(
        case,
        returncode=0,
        stdout="[0.91] cerebro/areas/atendimento/clara-operacao/regra -- Confirmação objetiva",
        stderr="query: confirmar agenda",
        latency_ms=125.0,
        tracked_paths=TRACKED,
    )
    assert result["passed"] is True
    assert result["expected_path_rank"] == 1
    assert result["matched_canonical_path"].endswith("regra.md")
    assert result["canonical_path_tracked"] is True
    assert "top_paths" not in result


def test_indexed_but_untracked_canonical_path_fails_closed():
    case = {
        "name": "Agenda",
        "query": "confirmar agenda",
        "expected_path_prefixes": ["cerebro/areas/atendimento/clara-operacao"],
        "max_rank": 3,
    }
    result = assess_gbrain_case(
        case,
        returncode=0,
        stdout="[0.91] cerebro/areas/atendimento/clara-operacao/regra -- Cache órfão",
        stderr="",
        latency_ms=5.0,
        tracked_paths={},
    )
    assert result["passed"] is False
    assert result["expected_path_rank"] == 1
    assert result["matched_canonical_path"] is None
    assert result["canonical_path_tracked"] is False


def test_semantically_unrelated_path_with_broad_keyword_fails_closed():
    case = {
        "name": "Agenda",
        "query": "confirmar agenda",
        "expected_path_prefixes": ["cerebro/areas/atendimento/clara-operacao"],
        "max_rank": 3,
    }
    result = assess_gbrain_case(
        case,
        returncode=0,
        stdout="[0.91] archive/clara-old/unrelated -- Cache antigo",
        stderr="",
        latency_ms=5.0,
        tracked_paths=TRACKED,
    )
    assert result["passed"] is False


def test_query_echo_or_stderr_signal_cannot_create_false_positive():
    case = {
        "name": "Financeiro",
        "query": "Omie boletos financeiro",
        "expected_path_prefixes": ["cerebro/areas/financeiro"],
        "max_rank": 3,
    }
    result = assess_gbrain_case(
        case,
        returncode=0,
        stdout="Query: Omie boletos financeiro\nNo results.",
        stderr="Omie boletos financeiro",
        latency_ms=5.0,
        tracked_paths={},
    )
    assert result["passed"] is False
    assert result["expected_path_rank"] is None


def test_nonzero_returncode_fails_even_with_tracked_match():
    case = {
        "name": "Agenda",
        "query": "confirmar agenda",
        "expected_path_prefixes": ["cerebro/areas/atendimento/clara-operacao"],
    }
    result = assess_gbrain_case(
        case,
        returncode=2,
        stdout="[0.91] cerebro/areas/atendimento/clara-operacao/regra -- fonte",
        stderr="erro",
        latency_ms=5.0,
        tracked_paths=TRACKED,
    )
    assert result["passed"] is False


def test_run_gbrain_fails_closed_when_executable_is_missing(tmp_path):
    case = {
        "name": "Resolver",
        "query": "resolver atendimento",
        "expected_path_prefixes": ["cerebro/gbrain/resolver"],
        "max_rank": 3,
    }
    result = run_gbrain(
        [case],
        canonical_root=tmp_path,
        executable="/definitely/missing/gbrain",
    )
    assert result["passed"] == 0
    assert result["results"][0]["error_type"] == "executable_not_found"
