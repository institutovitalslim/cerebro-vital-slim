from ivs_pgvector_bench.runner import assess_gbrain_case, run_gbrain


def test_assess_gbrain_case_requires_ranked_canonical_prefix_and_does_not_persist_paths():
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
    )
    assert result["passed"] is True
    assert result["expected_path_rank"] == 1
    assert "matched_expected_fragment" not in result
    assert "top_paths" not in result


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
    )
    assert result["passed"] is False
    assert result["expected_path_rank"] is None


def test_run_gbrain_fails_closed_when_executable_is_missing():
    case = {
        "name": "Resolver",
        "query": "resolver atendimento",
        "expected_path_prefixes": ["cerebro/gbrain/resolver"],
        "max_rank": 3,
    }
    result = run_gbrain([case], executable="/definitely/missing/gbrain")
    assert result["passed"] == 0
    assert result["results"][0]["error_type"] == "executable_not_found"
