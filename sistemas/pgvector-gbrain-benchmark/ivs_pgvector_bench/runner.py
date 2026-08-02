from __future__ import annotations

import argparse
import json
import os
import re
import signal
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

from .core import compute_metrics, decide, evaluate_gates
from .pgvector_backend import PgvectorBackend

_RESULT_PATH = re.compile(r"^\[[^\]]+\]\s+([^\s]+)\s+--", re.MULTILINE)


def assess_gbrain_case(
    case: dict,
    *,
    returncode: int,
    stdout: str,
    stderr: str,
    latency_ms: float,
    error_type: str | None = None,
    max_rank: int | None = None,
) -> dict:
    del stderr
    paths = _RESULT_PATH.findall(stdout)
    prefixes = [prefix.strip("/").lower() for prefix in case["expected_path_prefixes"]]
    rank = None
    for index, path in enumerate(paths, start=1):
        normalized = path.strip("/").lower()
        if any(normalized == prefix or normalized.startswith(prefix + "/") for prefix in prefixes):
            rank = index
            break
    effective_max_rank = max_rank if max_rank is not None else int(case.get("max_rank", 3))
    return {
        "name": case["name"],
        "query": case["query"],
        "passed": returncode == 0 and rank is not None and rank <= effective_max_rank,
        "returncode": returncode,
        "error_type": error_type,
        "expected_path_rank": rank,
        "result_count": len(paths),
        "latency_ms": round(latency_ms, 3),
    }


def _percentile(values: list[float], quantile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int((len(ordered) - 1) * quantile + 0.999999)))
    return round(float(ordered[index]), 3)


def _run_isolated(command: list[str], timeout_seconds: float) -> dict:
    try:
        process = subprocess.Popen(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
    except FileNotFoundError:
        return {"returncode": 127, "stdout": "", "stderr": "", "error_type": "executable_not_found"}
    except OSError:
        return {"returncode": 126, "stdout": "", "stderr": "", "error_type": "os_error"}
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
        return {"returncode": process.returncode, "stdout": stdout, "stderr": stderr, "error_type": None}
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        stdout, stderr = process.communicate()
        return {"returncode": 124, "stdout": stdout, "stderr": stderr, "error_type": "timeout"}


def run_gbrain(
    cases: list[dict],
    executable: str = "gbrain-ivs",
    timeout_seconds: float = 90.0,
    max_rank: int | None = None,
) -> dict:
    rows = []
    for case in cases:
        started = perf_counter()
        result = _run_isolated([executable, "search", case["query"]], timeout_seconds)
        rows.append(
            assess_gbrain_case(
                case,
                returncode=result["returncode"],
                stdout=result["stdout"],
                stderr=result["stderr"],
                latency_ms=(perf_counter() - started) * 1000,
                error_type=result["error_type"],
                max_rank=max_rank,
            )
        )
    latencies = [row["latency_ms"] for row in rows]
    passed = sum(1 for row in rows if row["passed"])
    return {
        "queries": len(rows),
        "passed": passed,
        "pass_rate": passed / len(rows) if rows else 0.0,
        "latency_p50_ms": _percentile(latencies, 0.50),
        "latency_p95_ms": _percentile(latencies, 0.95),
        "evaluation": "ranked_expected_path_top_k",
        "runtime_paths_persisted": False,
        "results": rows,
    }


def run_pgvector(dsn: str, docs: list[dict], queries: list[dict]) -> dict:
    backend = PgvectorBackend(dsn=dsn, dimensions=384)
    index_stats = backend.reset_and_index(docs)
    rows = []
    for item in queries:
        started = perf_counter()
        results = backend.search(item["query"], limit=3)
        latency_ms = (perf_counter() - started) * 1000
        rows.append(
            {
                "name": item["name"],
                "query": item["query"],
                "expected": item["expected"],
                "retrieved": [result["id"] for result in results],
                "scores": [round(result["score"], 6) for result in results],
                "latency_ms": round(latency_ms, 3),
            }
        )
    metrics = compute_metrics(rows)
    plan = backend.index_plan(queries[0]["query"], limit=3)
    return {
        **metrics,
        "documents": backend.count(),
        "index_ms": index_stats["index_ms"],
        "extension_version": backend.extension_version(),
        "embedding": "local-deterministic-hash-384d",
        "execution_plan": plan,
        "latency_scope": "micro_corpus_default_planner_not_hnsw_claim",
        "results": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark governado pgvector × GBrain para o IVS")
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--queries", type=Path, required=True)
    parser.add_argument("--gbrain-cases", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--dsn-env", default="IVS_BENCH_PGVECTOR_DSN")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    dsn = os.environ.get(args.dsn_env)
    if not dsn:
        parser.error(f"required DSN environment variable is missing: {args.dsn_env}")
    docs = json.loads(args.corpus.read_text(encoding="utf-8"))
    queries = json.loads(args.queries.read_text(encoding="utf-8"))
    cases = json.loads(args.gbrain_cases.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    thresholds = manifest["gates"]

    pgvector_result = run_pgvector(dsn, docs, queries)
    gbrain_result = run_gbrain(
        cases,
        max_rank=int(thresholds["gbrain_expected_path_max_rank"]),
    )
    gate_results = evaluate_gates(
        gbrain=gbrain_result,
        pgvector=pgvector_result,
        thresholds=thresholds,
    )
    decision_result = decide(
        gbrain=gbrain_result,
        pgvector=pgvector_result,
        gates=gate_results,
    )
    runtime_paths_persisted = any("top_paths" in row for row in gbrain_result["results"])
    payload = {
        "schema_version": 2,
        "generated_at": datetime.now(UTC).isoformat(),
        "safety": {
            "synthetic_pgvector_corpus": True,
            "gbrain_mode": "read_only_search",
            "runtime_paths_persisted": runtime_paths_persisted,
            "pii_persisted": runtime_paths_persisted,
            "production_modified": False,
            "dsn_validated_ephemeral_loopback": True,
        },
        "comparability_note": "Os corpora não são equivalentes: métricas de latência não autorizam comparação direta nem substituição arquitetural.",
        "gate_thresholds": thresholds,
        "gates": gate_results,
        "gbrain": gbrain_result,
        "pgvector": pgvector_result,
        "decision": decision_result,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "decision": decision_result["decision"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
