from __future__ import annotations

import hashlib
import math
import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass


def _normalize(text: str) -> str:
    folded = unicodedata.normalize("NFKD", text.lower())
    return " ".join("".join(ch for ch in folded if not unicodedata.combining(ch)).split())


def _features(text: str) -> Iterable[str]:
    normalized = _normalize(text)
    words = re.findall(r"[a-z0-9]+", normalized)
    for word in words:
        yield f"w:{word}"
        if len(word) >= 4:
            padded = f"^{word}$"
            for index in range(len(padded) - 2):
                yield f"c:{padded[index:index + 3]}"
    for index in range(len(words) - 1):
        yield f"b:{words[index]}_{words[index + 1]}"


@dataclass(frozen=True)
class HashEmbedding:
    dimensions: int = 384

    def embed(self, text: str) -> list[float]:
        if self.dimensions < 8:
            raise ValueError("dimensions must be >= 8")
        vector = [0.0] * self.dimensions
        for feature in _features(text):
            digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
            raw = int.from_bytes(digest, "big")
            index = raw % self.dimensions
            sign = 1.0 if (raw >> 8) & 1 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]


def _nearest_rank(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(1, math.ceil(percentile * len(ordered)))
    return float(ordered[rank - 1])


def compute_metrics(rows: list[dict]) -> dict:
    if not rows:
        return {
            "queries": 0,
            "recall_at_1": 0.0,
            "recall_at_3": 0.0,
            "mrr": 0.0,
            "latency_p50_ms": 0.0,
            "latency_p95_ms": 0.0,
        }
    reciprocal_ranks: list[float] = []
    hits_at_1 = 0
    hits_at_3 = 0
    for row in rows:
        expected = row["expected"]
        retrieved = row["retrieved"]
        if retrieved and retrieved[0] == expected:
            hits_at_1 += 1
        if expected in retrieved[:3]:
            hits_at_3 += 1
        try:
            rank = retrieved.index(expected) + 1
        except ValueError:
            rank = 0
        reciprocal_ranks.append(1.0 / rank if rank else 0.0)
    latencies = [float(row["latency_ms"]) for row in rows]
    total = len(rows)
    return {
        "queries": total,
        "recall_at_1": hits_at_1 / total,
        "recall_at_3": hits_at_3 / total,
        "mrr": sum(reciprocal_ranks) / total,
        "latency_p50_ms": _nearest_rank(latencies, 0.50),
        "latency_p95_ms": _nearest_rank(latencies, 0.95),
    }


def evaluate_gates(*, gbrain: dict, pgvector: dict, thresholds: dict) -> list[dict]:
    specs = [
        ("gbrain_pass_rate", gbrain.get("pass_rate", 0.0), ">=", thresholds["gbrain_pass_rate_min"], "operational_baseline"),
        ("pgvector_recall_at_3", pgvector.get("recall_at_3", 0.0), ">=", thresholds["pgvector_recall_at_3_min"], "synthetic_candidate"),
        ("pgvector_mrr", pgvector.get("mrr", 0.0), ">=", thresholds["pgvector_mrr_min"], "synthetic_candidate"),
        ("pgvector_latency_p95_ms", pgvector.get("latency_p95_ms", float("inf")), "<=", thresholds["pgvector_p95_ms_max"], "synthetic_candidate"),
    ]
    return [
        {
            "name": name,
            "observed": observed,
            "comparator": comparator,
            "threshold": threshold,
            "scope": scope,
            "passed": observed >= threshold if comparator == ">=" else observed <= threshold,
        }
        for name, observed, comparator, threshold, scope in specs
    ]


def decide(*, gbrain: dict, pgvector: dict, gates: list[dict]) -> dict:
    del gbrain, pgvector
    by_name = {gate["name"]: gate for gate in gates}
    gbrain_passed = by_name["gbrain_pass_rate"]["passed"]
    candidate_passed = all(
        gate["passed"] for gate in gates if gate["scope"] == "synthetic_candidate"
    )
    common = {
        "status": "DONE_WITH_CONCERNS",
        "gbrain_gate_status": "PASS" if gbrain_passed else "FAIL",
        "candidate_gate_status": "PASS_SYNTHETIC_ONLY" if candidate_passed else "FAIL",
        "requires_same_corpus_evidence": True,
        "requires_human_gate_before_production": True,
    }
    if not gbrain_passed:
        return {
            **common,
            "decision": "INVESTIGATE_GBRAIN_GAP_NO_STANDALONE_DECISION",
            "reason": "O GBrain falhou o gate operacional; o resultado sintético do pgvector não prova que uma camada separada resolva a lacuna.",
        }
    if not candidate_passed:
        return {
            **common,
            "decision": "KEEP_GBRAIN_NO_STANDALONE_PGVECTOR",
            "reason": "O candidato pgvector falhou um ou mais gates sintéticos e não deve avançar.",
        }
    return {
        **common,
        "decision": "KEEP_GBRAIN_NO_STANDALONE_PGVECTOR",
        "reason": "O candidato passou gates sintéticos, mas não demonstrou valor incremental no mesmo corpus do GBrain.",
    }
