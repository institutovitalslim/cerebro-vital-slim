import json
import re
import shutil
import string
from collections import Counter
from itertools import combinations, pairwise
from pathlib import Path

import pytest

from hook_intelligence.domain.models import AwarenessStage, Channel, Objective, Tone
from hook_intelligence.engine.library import ALLOWED_SLOTS, EXACT_MECHANISM_IDS, HookLibrary

DATA_ROOT = Path(__file__).resolve().parents[3] / "data"
PATTERN_FILES = ("universal/patterns.json", "ivs-health/patterns.json")
REQUIRED_CLAIM_CATEGORIES = {
    "cure",
    "guarantee",
    "diagnosis",
    "prescription",
    "false_urgency",
    "stigma",
    "unsourced_number",
    "absolute_superiority",
}


def normalized(text: str) -> str:
    return "".join(character for character in text.casefold() if character.isalnum())


def explanation_similarity(left: str, right: str) -> float:
    """Dice de bigramas lexicais; 0,72 separa estrutura editorial de texto formularizado."""

    def pairs(text: str) -> set[tuple[str, str]]:
        return set(pairwise(re.findall(r"\w+", text.casefold())))

    left_pairs, right_pairs = pairs(left), pairs(right)
    return 2 * len(left_pairs & right_pairs) / (len(left_pairs) + len(right_pairs))


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


def copied_data(tmp_path: Path) -> Path:
    root = tmp_path / "data"
    shutil.copytree(DATA_ROOT, root)
    return root


def write_json(path: Path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def test_exact_mechanism_contract_and_data():
    library = HookLibrary.load_default()
    assert len(EXACT_MECHANISM_IDS) == 20
    assert set(library.mechanisms) == EXACT_MECHANISM_IDS


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("invented_mechanism", "IDs devem ser exatamente"),
        ("thirty_nine_universal", "ao menos 40"),
        ("missing_universal_mechanism", "mechanism_reveal"),
        ("ivs_under_ten_mechanisms", "ao menos 10 mecanismos"),
    ],
)
def test_loader_rejects_mutated_mechanism_coverage(tmp_path, mutation, expected):
    root = copied_data(tmp_path)
    mechanism_path = root / "universal/mechanisms.json"
    universal_path = root / "universal/patterns.json"
    ivs_path = root / "ivs-health/patterns.json"
    mechanisms = json.loads(mechanism_path.read_text(encoding="utf-8"))
    universal = json.loads(universal_path.read_text(encoding="utf-8"))
    ivs = json.loads(ivs_path.read_text(encoding="utf-8"))
    if mutation == "invented_mechanism":
        mechanisms[-1]["id"] = "invented_mechanism"
        write_json(mechanism_path, mechanisms)
    elif mutation == "thirty_nine_universal":
        universal.pop()
        write_json(universal_path, universal)
    elif mutation == "missing_universal_mechanism":
        for record in universal:
            if record["mechanism"] == "mechanism_reveal":
                record["mechanism"] = "curiosity_gap"
        write_json(universal_path, universal)
    else:
        retained = set(EXACT_MECHANISM_IDS) - {
            "avoidable_loss",
            "future_desire",
            "inverted_objection",
            "demonstration",
            "discovery",
            "incomplete_list",
            "editorial_question",
            "open_story",
            "grounded_contrarian",
            "mechanism_reveal",
            "before_after_tension",
        }
        for record in ivs:
            if record["mechanism"] not in retained:
                record["mechanism"] = "curiosity_gap"
        write_json(ivs_path, ivs)
    with pytest.raises(ValueError, match=expected):
        HookLibrary.load(root)


@pytest.mark.parametrize("bad_id", ["universal-", "wrong-curiosity-01", "UNIVERSAL-ok"])
def test_pattern_id_must_match_strict_slug_and_library_prefix(tmp_path, bad_id):
    root = copied_data(tmp_path)
    path = root / "universal/patterns.json"
    records = json.loads(path.read_text(encoding="utf-8"))
    records[0]["id"] = bad_id
    write_json(path, records)
    with pytest.raises(ValueError, match="id.*formato"):
        HookLibrary.load(root)


def test_loader_rejects_duplicate_and_short_explanations(tmp_path):
    root = copied_data(tmp_path)
    path = root / "universal/patterns.json"
    records = json.loads(path.read_text(encoding="utf-8"))
    records[1]["explanation"] = "  " + records[0]["explanation"].upper() + "  "
    write_json(path, records)
    with pytest.raises(ValueError, match="explanation.*duplicada.*universal-curiosity-gap-01"):
        HookLibrary.load(root)
    records[1]["explanation"] = "Explicação curta demais para orientar o uso editorial."
    write_json(path, records)
    with pytest.raises(ValueError, match="explanation.*180"):
        HookLibrary.load(root)


def test_loader_rejects_near_duplicate_explanation_and_names_both_ids(tmp_path):
    root = copied_data(tmp_path)
    path = root / "universal/patterns.json"
    records = json.loads(path.read_text(encoding="utf-8"))
    first_id, second_id = records[0]["id"], records[1]["id"]
    records[1]["explanation"] = records[0]["explanation"].replace(
        "detalhe negligenciado", "aspecto negligenciado"
    )
    write_json(path, records)

    with pytest.raises(ValueError) as error:
        HookLibrary.load(root)

    message = str(error.value)
    assert "explanation" in message and "similar" in message
    assert first_id in message and second_id in message


def test_all_explanations_are_editorial_and_unique_after_normalization():
    explanations = [pattern.explanation for pattern in HookLibrary.load_default().all_patterns]
    assert all(len(text) >= 180 for text in explanations)
    assert all(2 <= len(re.findall(r"[.!?](?:\s|$)", text)) <= 3 for text in explanations)
    assert all("..." not in text and "…" not in text for text in explanations)
    assert len({normalized(text) for text in explanations}) == len(explanations) == 60
    scores = [explanation_similarity(left, right) for left, right in combinations(explanations, 2)]
    assert max(scores) < 0.72


def test_explanation_similarity_flags_a_formularized_synthetic_pair():
    first = (
        "A abertura apresenta o tema, introduz um contraste e deixa uma pergunta sem resposta. "
        "A tensão é fechada pelo critério final, por isso funciona em conteúdos educativos."
    )
    second = (
        "A abertura apresenta o assunto, introduz um contraste e deixa uma pergunta sem resposta. "
        "A tensão é fechada pelo critério final, por isso funciona em conteúdos educativos."
    )
    assert explanation_similarity(first, second) >= 0.72


def test_loader_rejects_near_duplicate_template_and_names_both_ids(tmp_path):
    root = copied_data(tmp_path)
    path = root / "universal/patterns.json"
    records = json.loads(path.read_text(encoding="utf-8"))
    records[1]["template"] = records[0]["template"] + " agora"
    records[1]["slots"] = records[0]["slots"]
    write_json(path, records)
    with pytest.raises(ValueError) as error:
        HookLibrary.load(root)
    message = str(error.value)
    assert "similar" in message
    assert records[0]["id"] in message and records[1]["id"] in message


def test_auxiliary_datasets_are_loaded_validated_and_read_only():
    library = HookLibrary.load_default()
    assert isinstance(library.audiences, tuple) and len(library.audiences) >= 8
    assert isinstance(library.topics, tuple) and len(library.topics) >= 12
    assert set(library.forbidden_claims) == {"version", "categories"}
    assert {
        category["id"] for category in library.forbidden_claims["categories"]
    } == REQUIRED_CLAIM_CATEGORIES
    with pytest.raises(TypeError):
        library.forbidden_claims["version"] = "mutated"
    with pytest.raises(TypeError):
        library.audiences[0]["label"] = "mutated"


@pytest.mark.parametrize(
    ("relative", "mutation", "expected"),
    [
        ("ivs-health/audiences.json", "empty_object", "deve ser uma lista"),
        ("ivs-health/audiences.json", "duplicate_id", "ID duplicado"),
        ("ivs-health/forbidden-claims.json", "missing_category", "categorias"),
        ("ivs-health/forbidden-claims.json", "invalid_regex", "regex"),
    ],
)
def test_loader_rejects_invalid_auxiliary_data(tmp_path, relative, mutation, expected):
    root = copied_data(tmp_path)
    path = root / relative
    payload = json.loads(path.read_text(encoding="utf-8"))
    if mutation == "empty_object":
        payload = {}
    elif mutation == "duplicate_id":
        payload[1]["id"] = payload[0]["id"]
    elif mutation == "missing_category":
        payload["categories"].pop()
    else:
        payload["categories"][0]["patterns"] = ["("]
    write_json(path, payload)
    with pytest.raises(ValueError, match=expected):
        HookLibrary.load(root)


def test_forbidden_claim_patterns_detect_each_risk_and_clear_all_ivs_templates():
    library = HookLibrary.load_default()
    probes = {
        "cure": "Este protocolo cura a diabetes.",
        "guarantee": "Resultado garantido para todas as pessoas.",
        "diagnosis": "Você tem depressão.",
        "prescription": "Tome 20 mg deste composto diariamente.",
        "false_urgency": "Compre agora ou será tarde demais.",
        "stigma": "Só não emagrece quem é preguiçoso.",
        "unsourced_number": "Este método reduz 73% do colesterol.",
        "absolute_superiority": "Esta é a única solução que funciona.",
    }
    compiled = {
        category["id"]: [re.compile(pattern, re.IGNORECASE) for pattern in category["patterns"]]
        for category in library.forbidden_claims["categories"]
    }
    for category_id, phrase in probes.items():
        assert any(regex.search(phrase) for regex in compiled[category_id]), category_id
    for pattern in library.patterns("ivs-health"):
        matches = [
            category_id
            for category_id, regexes in compiled.items()
            if any(regex.search(pattern.template) for regex in regexes)
        ]
        assert not matches, (pattern.id, matches)


def test_five_regressions_render_slots_as_independent_phrases():
    library = HookLibrary.load_default()
    values = {
        "topic": "planejamento editorial",
        "audience": "equipes criteriosas",
        "desired_outcome": "decisões mais consistentes",
        "context": "na revisão semanal",
        "required_word": "evidência",
    }
    expected = {
        "universal-avoidable-loss-01": "O custo invisível de discutir planejamento editorial sem alinhar o objetivo: “decisões mais consistentes”",
        "universal-future-desire-02": "Um caminho possível para sua rotina — objetivo: decisões mais consistentes",
        "universal-discovery-02": "Uma perspectiva sobre planejamento editorial que ganha sentido com este contexto: na revisão semanal",
        "universal-incomplete-list-01": "Há três filtros úteis para avaliar planejamento editorial; o último considera este público: equipes criteriosas",
        "ivs-avoidable-loss-11": "Público: equipes criteriosas. O ruído evitável ao conferir a fonte antes de compartilhar planejamento editorial",
    }
    rendered = {}
    for pattern_id in expected:
        pattern = library.get(pattern_id)
        assert pattern is not None
        rendered[pattern_id] = pattern.template.format(**values)
    assert rendered == expected


@pytest.mark.parametrize(
    "values",
    [
        {
            "topic": "sono",
            "audience": "mulheres adultas",
            "desired_outcome": "decisões mais conscientes",
            "context": "na rotina diária",
            "required_word": "rotina",
        },
        {
            "topic": "comunicação",
            "audience": "uma pessoa cuidadosa",
            "desired_outcome": "uma escolha segura",
            "context": "no planejamento mensal",
            "required_word": "critério",
        },
        {
            "topic": "fontes confiáveis",
            "audience": "profissionais atentos",
            "desired_outcome": "leituras responsáveis",
            "context": "quando a informação ainda precisa ser verificada",
            "required_word": "fonte",
        },
    ],
)
def test_every_template_renders_cleanly_in_three_grammatical_scenarios(values):
    for pattern in HookLibrary.load_default().all_patterns:
        rendered = pattern.template.format(**values)
        assert "{" not in rendered and "}" not in rendered
        assert not re.search(r"\s{2,}", rendered)
        assert len(rendered) <= 280


def test_templates_avoid_known_slot_agreement_traps():
    templates = {
        pattern.id: pattern.template for pattern in HookLibrary.load_default().all_patterns
    }
    forbidden = {
        "desired_outcome": re.compile(
            r"\{desired_outcome\}\s+(?:significa\b|(?:mais\s+)?(?:coerente|claro|clara|"
            r"possível|seguro|segura|adequado|adequada)\b)",
            re.IGNORECASE,
        ),
        "context": re.compile(r"\b(?:para|em|no|na|pelo|pela)\s+\{context\}", re.IGNORECASE),
        "audience": re.compile(
            r"\{audience\}\s+(?:é|são|pode|podem|deve|devem|precisa|precisam|"
            r"ao\s+\w+|foi|foram)|(?:por|para)\s+\{audience\}\s+ao\b",
            re.IGNORECASE,
        ),
    }
    violations = [
        (pattern_id, slot)
        for pattern_id, template in templates.items()
        for slot, expression in forbidden.items()
        if expression.search(template)
    ]
    assert violations == []
