from __future__ import annotations

import re
import subprocess
from pathlib import Path

_RESULT_PATH = re.compile(r"^\[[^\]]+\]\s+([^\s]+)\s+--", re.MULTILINE)


def normalize_canonical_path(value: str) -> str:
    return value.strip("/").lower().removesuffix(".md")


def build_tracked_path_index(canonical_root: Path) -> dict[str, str]:
    """Mapeia slugs normalizados para arquivos existentes e rastreados pelo Git."""
    proc = subprocess.run(
        ["git", "-C", str(canonical_root), "ls-files", "-z"],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return {}

    tracked: dict[str, str] = {}
    for relative in proc.stdout.split("\0"):
        if not relative:
            continue
        if (canonical_root / relative).is_file():
            tracked[normalize_canonical_path(relative)] = relative
    return tracked


def assess_ranked_canonical_path(
    case: dict,
    *,
    returncode: int,
    stdout: str,
    tracked_paths: dict[str, str],
    max_rank: int | None = None,
) -> dict:
    """Avalia Top-K e falha se o resultado não existir no corpus Git rastreado."""
    result_paths = [normalize_canonical_path(path) for path in _RESULT_PATH.findall(stdout)]
    prefixes = [normalize_canonical_path(prefix) for prefix in case["expected_path_prefixes"]]
    rank = None
    matched_slug = None
    for index, path in enumerate(result_paths, start=1):
        if any(path == prefix or path.startswith(prefix + "/") for prefix in prefixes):
            rank = index
            matched_slug = path
            break

    effective_max_rank = max_rank if max_rank is not None else int(case.get("max_rank", 3))
    matched_canonical_path = tracked_paths.get(matched_slug or "")
    canonical_path_tracked = matched_canonical_path is not None
    return {
        "passed": (
            returncode == 0
            and rank is not None
            and rank <= effective_max_rank
            and canonical_path_tracked
        ),
        "returncode": returncode,
        "expected_path_rank": rank,
        "max_rank": effective_max_rank,
        "matched_canonical_path": matched_canonical_path,
        "canonical_path_tracked": canonical_path_tracked,
        "result_count": len(result_paths),
    }
