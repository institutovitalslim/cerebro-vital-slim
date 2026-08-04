import json
import re
import shutil
import string
from collections import Counter
from pathlib import Path

import pytest

from hook_intelligence.domain.models import AwarenessStage, Channel, Objective, Tone
from hook_intelligence.engine.library import ALLOWED_SLOTS, HookLibrary

DATA_ROOT = Path(__file__).resolve().parents[3] / "data"
PATTERN_FILES = ("universal/patterns.json", "ivs-health/patterns.json")


def normalized(text: str) -> str:
    return "".join(character for character in text.casefold() if character.isalnum())


def test_load_default_is_independent_from_working_directory(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    library = HookLibrary.load_default()
    assert len(library.all_patterns) >= 60


def test_library_minimum_counts_and_globally_unique_ids():
    library = HookLibrary.load_default()
    assert len(library.patterns("universal")) >= 40
    assert len(library.patterns("ivs-health")) >= 20
    ids = [pattern.id for pattern in library.all_patterns]
    assert len(ids) == len(set(ids))


def test_mechanism_coverage():
    library = HookLibrary.load_default()
    assert len(library.mechanisms) == 20
    assert {pattern.mechanism for pattern in library.patterns("universal")} == set(
        library.mechanisms
    )
    assert len({pattern.mechanism for pattern in library.patterns("ivs-health")}) >= 10


def test_patterns_have_exact_allowed_slots_and_explanations():
    library = HookLibrary.load_default()
    formatter = string.Formatter()
    for pattern in library.all_patterns:
        extracted = tuple(
            field_name
            for _, field_name, _, _ in formatter.parse(pattern.template)
            if field_name is not None
        )
        assert pattern.slots
        assert pattern.slots == extracted
        assert set(pattern.slots) <= ALLOWED_SLOTS
        assert len(pattern.explanation) >= 40


def test_references_match_taxonomies_and_domain_enums():
    library = HookLibrary.load_default()
    expected = {
        "channels": {item.value for item in Channel},
        "objectives": {item.value for item in Objective},
        "awareness": {item.value for item in AwarenessStage},
        "tones": {item.value for item in Tone},
    }
    assert {name: set(values) for name, values in library.taxonomies.items()} == expected
    for pattern in library.all_patterns:
        assert set(pattern.channels) <= expected["channels"]
        assert set(pattern.objectives) <= expected["objectives"]
        assert set(pattern.awareness_stages) <= expected["awareness"]
        assert set(pattern.tones) <= expected["tones"]


def test_templates_are_globally_unique_after_normalization():
    templates = [
        normalized(pattern.template) for pattern in HookLibrary.load_default().all_patterns
    ]
    assert len(templates) == len(set(templates))


def test_get_and_combined_filter_are_deterministic():
    library = HookLibrary.load_default()
    selected = library.filter(
        library="universal",
        channel="reel",
        objective="curiosity",
        awareness_stage="problem_aware",
        tone="educational",
        mechanism="curiosity_gap",
        max_intensity=2,
    )
    assert selected
    assert selected == library.filter(
        library="universal",
        channel="reel",
        objective="curiosity",
        awareness_stage="problem_aware",
        tone="educational",
        mechanism="curiosity_gap",
        max_intensity=2,
    )
    assert selected == tuple(sorted(selected, key=lambda pattern: pattern.id))
    assert all(
        pattern.library == "universal"
        and "reel" in pattern.channels
        and "curiosity" in pattern.objectives
        and "problem_aware" in pattern.awareness_stages
        and "educational" in pattern.tones
        and pattern.mechanism == "curiosity_gap"
        and pattern.intensity <= 2
        for pattern in selected
    )
    assert library.get(selected[0].id) is selected[0]
    assert library.get("missing-id") is None


@pytest.mark.parametrize("invalid_kind", ["unknown_slot", "duplicate_id"])
def test_invalid_data_has_descriptive_file_id_and_field(tmp_path, invalid_kind):
    root = tmp_path / "data"
    shutil.copytree(DATA_ROOT, root)
    path = root / "ivs-health" / "patterns.json"
    records = json.loads(path.read_text(encoding="utf-8"))
    invalid_id = records[0]["id"]
    if invalid_kind == "unknown_slot":
        records[0]["template"] = (
            "Uma análise segura de {forbidden_slot} para orientar escolhas conscientes"
        )
        records[0]["slots"] = ["forbidden_slot"]
        expected = "slots"
    else:
        records[1]["id"] = invalid_id
        expected = "id"
    path.write_text(json.dumps(records, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(ValueError) as error:
        HookLibrary.load(root)

    message = str(error.value)
    assert "ivs-health/patterns.json" in message
    assert invalid_id in message
    assert expected in message


def test_all_json_and_supporting_ivs_datasets():
    for path in DATA_ROOT.rglob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
    audiences = json.loads((DATA_ROOT / "ivs-health/audiences.json").read_text(encoding="utf-8"))
    topics = json.loads((DATA_ROOT / "ivs-health/topics.json").read_text(encoding="utf-8"))
    forbidden = json.loads(
        (DATA_ROOT / "ivs-health/forbidden-claims.json").read_text(encoding="utf-8")
    )
    assert len(audiences) >= 8
    assert len(topics) >= 12
    assert forbidden["version"]
    required = {
        "cure",
        "guarantee",
        "diagnosis",
        "prescription",
        "false_urgency",
        "stigma",
        "unsourced_number",
        "absolute_superiority",
    }
    assert required <= {category["id"] for category in forbidden["categories"]}


def test_ivs_patterns_avoid_obvious_health_claims():
    texts = [
        pattern.template.casefold() for pattern in HookLibrary.load_default().patterns("ivs-health")
    ]
    forbidden = re.compile(
        r"\b(?:cur(?:e|a)(?:r|do|da)?|garantia de resultado|perca \d+\s*kg|"
        r"você tem [a-zá-ú]+|tome [a-zá-ú]+|use \d+\s*(?:mg|ml))\b"
    )
    assert not [text for text in texts if forbidden.search(text)]


def test_real_counts_are_visible_for_diagnostics():
    library = HookLibrary.load_default()
    assert Counter(pattern.library for pattern in library.all_patterns) == {
        "universal": 40,
        "ivs-health": 20,
    }
