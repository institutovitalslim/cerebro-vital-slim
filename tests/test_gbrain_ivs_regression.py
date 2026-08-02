from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "gbrain_ivs_regression.py"
SPEC = importlib.util.spec_from_file_location("gbrain_ivs_regression", SCRIPT)
assert SPEC and SPEC.loader
REGRESSION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REGRESSION)

TRACKED = {
    "cerebro/areas/atendimento/referencias/clara/confirmacao-agenda": (
        "cerebro/areas/atendimento/referencias/clara/confirmacao-agenda.md"
    ),
    "cerebro/gbrain/resolver": "cerebro/gbrain/RESOLVER.md",
}


def test_assess_result_accepts_tracked_canonical_prefix_in_top_three() -> None:
    case = {
        "expected_path_prefixes": ["cerebro/areas/atendimento/referencias/clara/confirmacao-agenda"],
        "max_rank": 3,
    }
    stdout = (
        "[0.99] cerebro/logs/outro -- ruído\n"
        "[0.95] cerebro/areas/atendimento/referencias/clara/confirmacao-agenda -- fonte"
    )

    result = REGRESSION.assess_result(
        case,
        returncode=0,
        stdout=stdout,
        stderr="",
        tracked_paths=TRACKED,
    )

    assert result["passed"] is True
    assert result["expected_path_rank"] == 2
    assert result["matched_canonical_path"].endswith("confirmacao-agenda.md")


def test_assess_result_rejects_keywords_in_wrong_path_and_stderr() -> None:
    case = {
        "expected_path_prefixes": ["cerebro/areas/marketing/referencias/joao/marketing-reels"],
        "max_rank": 3,
    }
    stdout = "[1.00] cerebro/logs/marketing-reels -- João marketing reels relatório"
    stderr = "cerebro/areas/marketing/referencias/joao/marketing-reels"

    result = REGRESSION.assess_result(
        case,
        returncode=0,
        stdout=stdout,
        stderr=stderr,
        tracked_paths={},
    )

    assert result["passed"] is False
    assert result["expected_path_rank"] is None


def test_assess_result_rejects_expected_path_below_rank_limit() -> None:
    case = {
        "expected_path_prefixes": ["cerebro/gbrain/resolver"],
        "max_rank": 3,
    }
    stdout = (
        "[1.00] cerebro/logs/a -- a\n"
        "[0.90] cerebro/logs/b -- b\n"
        "[0.80] cerebro/logs/c -- c\n"
        "[0.70] cerebro/gbrain/resolver -- fonte canônica"
    )

    result = REGRESSION.assess_result(
        case,
        returncode=0,
        stdout=stdout,
        stderr="",
        tracked_paths=TRACKED,
    )

    assert result["passed"] is False
    assert result["expected_path_rank"] == 4


def test_assess_result_rejects_indexed_but_untracked_path() -> None:
    case = {
        "expected_path_prefixes": ["cerebro/gbrain/resolver"],
        "max_rank": 3,
    }
    result = REGRESSION.assess_result(
        case,
        returncode=0,
        stdout="[1.00] cerebro/gbrain/resolver -- cache órfão",
        stderr="",
        tracked_paths={},
    )

    assert result["passed"] is False
    assert result["expected_path_rank"] == 1
    assert result["canonical_path_tracked"] is False


def test_assess_result_rejects_nonzero_returncode() -> None:
    case = {"expected_path_prefixes": ["cerebro/gbrain/resolver"], "max_rank": 3}
    result = REGRESSION.assess_result(
        case,
        returncode=2,
        stdout="[1.00] cerebro/gbrain/resolver -- fonte",
        stderr="erro",
        tracked_paths=TRACKED,
    )
    assert result["passed"] is False


def test_run_search_timeout_fails_closed_with_text_output(monkeypatch) -> None:
    def raise_timeout(*args, **kwargs):
        del args, kwargs
        raise REGRESSION.subprocess.TimeoutExpired(
            cmd=["gbrain-ivs", "search"],
            timeout=60,
            output=b"[1.00] cerebro/gbrain/resolver -- parcial",
        )

    monkeypatch.setattr(REGRESSION.subprocess, "run", raise_timeout)
    result = REGRESSION.run_search("resolver")

    assert result == {"returncode": 124, "stdout": "", "stderr": "timeout"}
