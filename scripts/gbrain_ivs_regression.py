#!/usr/bin/env python3
"""Checklist de regressão do GBrain IVS.

Valida se o sidecar encontra fontes canônicas rastreadas que os agentes devem abrir antes de responder.
Retorna código 0 apenas quando todos os cenários mínimos passam.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("IVS_BRAIN_ROOT", str(SCRIPT_ROOT))).resolve()
REPORT_DIR = Path(os.environ.get("IVS_GBRAIN_REPORT_DIR", "/root/.local/share/ivs-gbrain/reports"))
CANONICAL_LATEST = ROOT / "cerebro/gbrain/sync/latest-regression.md"
GBRAIN_REPO = Path(
    os.environ.get("IVS_GBRAIN_REPO", "/root/cerebro-vital-slim/tmp/repo-reverse/gbrain")
)
BENCHMARK_ROOT = ROOT / "sistemas/pgvector-gbrain-benchmark"
CASES_PATH = BENCHMARK_ROOT / "data/gbrain_cases.json"
sys.path.insert(0, str(BENCHMARK_ROOT))

from ivs_pgvector_bench.gbrain_eval import (
    assess_ranked_canonical_path,
    build_tracked_path_index,
)

ENV = os.environ.copy()
ENV["GBRAIN_HOME"] = "/root/.local/share/ivs-gbrain/home"
ENV["OPENCLAW_WORKSPACE"] = "/root/.local/share/ivs-gbrain/agent-workspace"
ENV["PATH"] = "/tmp/gbrain-ivs-bin:/root/.bun/bin:" + ENV.get("PATH", "")


def load_cases() -> list[dict]:
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))


def assess_result(
    case: dict,
    *,
    returncode: int,
    stdout: str,
    stderr: str,
    tracked_paths: dict[str, str],
) -> dict:
    del stderr
    return assess_ranked_canonical_path(
        case,
        returncode=returncode,
        stdout=stdout,
        tracked_paths=tracked_paths,
    )


def run_search(query: str) -> dict:
    try:
        proc = subprocess.run(
            ["gbrain-ivs", "search", query],
            cwd=str(GBRAIN_REPO),
            env=ENV,
            text=True,
            capture_output=True,
            timeout=60,
            check=False,
        )
        return {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
    except subprocess.TimeoutExpired:
        return {"returncode": 124, "stdout": "", "stderr": "timeout"}
    except FileNotFoundError:
        return {"returncode": 127, "stdout": "", "stderr": "gbrain-ivs not found"}
    except OSError as exc:
        return {"returncode": 126, "stdout": "", "stderr": str(exc)}


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).isoformat()
    tracked_paths = build_tracked_path_index(ROOT)
    results = []
    for case in load_cases():
        response = run_search(case["query"])
        assessment = assess_result(
            case,
            returncode=response["returncode"],
            stdout=response["stdout"],
            stderr=response["stderr"],
            tracked_paths=tracked_paths,
        )
        results.append({**case, **assessment})

    ok = all(result["passed"] for result in results)
    payload = {"ok": ok, "generated_at": generated_at, "results": results}
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    json_path = REPORT_DIR / f"gbrain-ivs-regression-{stamp}.json"
    md_path = REPORT_DIR / f"gbrain-ivs-regression-{stamp}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# GBrain IVS — Regressão de Agentes",
        "",
        f"Gerado em: `{generated_at}`",
        "",
        f"Status geral: **{'OK' if ok else 'FALHA'}**",
        "",
    ]
    for result in results:
        status = "OK" if result["passed"] else "FALHA"
        rank = result["expected_path_rank"] if result["expected_path_rank"] is not None else "—"
        path = result["matched_canonical_path"] or "—"
        lines.append(
            f"- {status} — **{result['name']}** — rank `{rank}` — `{path}`"
        )
    lines += [
        "",
        "## Uso operacional",
        "O checklist só aprova fontes encontradas no Top 3 que também existam e estejam rastreadas no Git canônico.",
    ]
    markdown = "\n".join(lines).strip() + "\n"
    md_path.write_text(markdown, encoding="utf-8")
    CANONICAL_LATEST.parent.mkdir(parents=True, exist_ok=True)
    CANONICAL_LATEST.write_text(markdown, encoding="utf-8")
    (REPORT_DIR / "latest-regression.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (REPORT_DIR / "latest-regression.md").write_text(markdown, encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": ok,
                "report": str(md_path),
                "canonical_latest": str(CANONICAL_LATEST),
                "passed": sum(1 for result in results if result["passed"]),
                "total": len(results),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
