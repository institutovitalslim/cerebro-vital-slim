from copy import deepcopy
from types import SimpleNamespace

import pytest

from hook_intelligence.domain.models import ComplianceStatus, GenerationRequest, Library
from hook_intelligence.engine.compliance import CLAIM_SCAN_MAX_CHARS, evaluate_compliance
from hook_intelligence.engine.library import HookLibrary, Pattern
from hook_intelligence.engine.pipeline import generate_deterministic


@pytest.fixture(scope="module")
def rules() -> HookLibrary:
    return HookLibrary.load_default()


@pytest.mark.parametrize(
    ("text", "status", "reasons"),
    [
        ("Você vai perder 10 kg em 30 dias", ComplianceStatus.BLOCK, ["GUARANTEED_RESULT"]),
        ("Cure a obesidade definitivamente", ComplianceStatus.BLOCK, ["CURE_CLAIM"]),
        (
            "Este tratamento funciona para todas as pacientes",
            ComplianceStatus.BLOCK,
            ["GUARANTEED_RESULT"],
        ),
        (
            "Este método reduz 37% da gordura",
            ComplianceStatus.REVIEW,
            ["UNSOURCED_CLINICAL_NUMBER"],
        ),
        (
            "Por que o sono pode influenciar suas escolhas alimentares?",
            ComplianceStatus.PASS,
            [],
        ),
    ],
)
def test_required_plan_examples(rules, text, status, reasons):
    result = evaluate_compliance(text, Library.IVS_HEALTH, rules)
    assert result.status is status
    assert result.reasons == reasons


@pytest.mark.parametrize(
    ("text", "reason", "status"),
    [
        ("Resultado garantido para todas as pessoas.", "GUARANTEED_RESULT", ComplianceStatus.BLOCK),
        ("Este protocolo cura a diabetes.", "CURE_CLAIM", ComplianceStatus.BLOCK),
        ("Você tem diabetes.", "DIRECT_DIAGNOSIS", ComplianceStatus.BLOCK),
        ("Tome 2 cápsulas por dia.", "DIRECT_PRESCRIPTION", ComplianceStatus.BLOCK),
        ("Compre agora ou será tarde demais.", "FALSE_URGENCY", ComplianceStatus.BLOCK),
        ("Só não emagrece quem é preguiçoso.", "STIGMATIZING_LANGUAGE", ComplianceStatus.BLOCK),
        (
            "Este método reduz 73% do colesterol.",
            "UNSOURCED_CLINICAL_NUMBER",
            ComplianceStatus.REVIEW,
        ),
        (
            "Esta é a única solução que funciona.",
            "ABSOLUTE_SUPERIORITY",
            ComplianceStatus.BLOCK,
        ),
    ],
)
def test_category_matrix(rules, text, reason, status):
    result = evaluate_compliance(text, "ivs-health", rules)
    assert result.status is status
    assert result.reasons == [reason]


@pytest.mark.parametrize(
    "text",
    [
        "Este conteúdo não promete cura nem resultado garantido.",
        "Não existe solução universal.",
        "Resultados individuais podem variar.",
        "Você tem dúvidas sobre o tema?",
        "Use esta estrutura no início do vídeo.",
    ],
)
def test_editorial_false_positives_pass(rules, text):
    assert evaluate_compliance(text, "ivs-health", rules).status is ComplianceStatus.PASS


def test_normalization_is_nfkc_case_and_whitespace_aware_without_mutating(rules):
    text = "  ＶＯＣÊ\tVAI\nPERDER 10 KG EM 30 DIAS  "
    before = text
    result = evaluate_compliance(text, "ivs-health", rules)
    assert result.status is ComplianceStatus.BLOCK
    assert result.reasons == ["GUARANTEED_RESULT"]
    assert text == before


@pytest.mark.parametrize("text", ["cura", "CÚRE", "Cure a obesidade definitivamente"])
def test_accents_and_conservative_cure_detection(rules, text):
    result = evaluate_compliance(text, "ivs-health", rules)
    if text == "Cure a obesidade definitivamente":
        assert result.status is ComplianceStatus.BLOCK
    else:
        assert result.status is ComplianceStatus.PASS


@pytest.mark.parametrize("text", ["a\x00b", "a\u200bb", "a\u202eb"])
def test_control_format_and_bidi_characters_are_rejected(rules, text):
    with pytest.raises(ValueError, match="Unicode.*categoria C"):
        evaluate_compliance(text, "ivs-health", rules)


@pytest.mark.parametrize("text", [None, 123, b"texto"])
def test_non_string_is_rejected(rules, text):
    with pytest.raises(ValueError, match="text.*str"):
        evaluate_compliance(text, "ivs-health", rules)  # type: ignore[arg-type]


@pytest.mark.parametrize("text", ["", " \t\n ", "!? —"])
def test_semantically_empty_text_is_rejected(rules, text):
    with pytest.raises(ValueError, match="alfanumérico"):
        evaluate_compliance(text, "ivs-health", rules)


def test_length_boundary(rules):
    assert evaluate_compliance("a" * CLAIM_SCAN_MAX_CHARS, "ivs-health", rules).status == "pass"
    with pytest.raises(ValueError, match=str(CLAIM_SCAN_MAX_CHARS)):
        evaluate_compliance("a" * (CLAIM_SCAN_MAX_CHARS + 1), "ivs-health", rules)


@pytest.mark.parametrize("library", ["invalid", "IVS-health", 1, None])
def test_invalid_library_is_rejected(rules, library):
    with pytest.raises(ValueError, match="library"):
        evaluate_compliance("texto válido", library, rules)  # type: ignore[arg-type]


def test_universal_validates_text_but_always_passes():
    result = evaluate_compliance("Você vai perder 10 kg em 30 dias", Library.UNIVERSAL)
    assert result.status is ComplianceStatus.PASS
    assert result.reasons == []
    with pytest.raises(ValueError):
        evaluate_compliance("\u200b", Library.UNIVERSAL)


def test_block_precedes_review_and_reasons_are_unique_in_dataset_order(rules):
    text = (
        "Resultado garantido para todas as pessoas: reduz 37% da gordura. "
        "Você tem diabetes. Resultado garantido para todas as pessoas."
    )
    result = evaluate_compliance(text, "ivs-health", rules)
    assert result.status is ComplianceStatus.BLOCK
    assert result.reasons == [
        "GUARANTEED_RESULT",
        "DIRECT_DIAGNOSIS",
        "UNSOURCED_CLINICAL_NUMBER",
    ]


def _pattern(pattern_id: str, template: str, library: str = "ivs-health") -> Pattern:
    slots = tuple(
        slot
        for slot in ("topic", "audience", "desired_outcome", "context", "required_word")
        if "{" + slot + "}" in template
    )
    return Pattern(
        pattern_id,
        library,
        "curiosity_gap",
        ("retention",),
        ("reel",),
        ("problem_aware",),
        ("premium",),
        template,
        slots,
        "Explicação editorial segura e suficiente para o teste de integração local.",
        1,
    )


def _request(**updates) -> GenerationRequest:
    values = {
        "topic": "sono",
        "audience": "mulheres adultas",
        "channel": "reel",
        "objective": "retention",
        "library": "ivs-health",
        "count": 1,
    }
    values.update(updates)
    return GenerationRequest(**values)  # type: ignore[arg-type]


def test_pipeline_blocks_claims_with_fake_library_and_does_not_mutate_request():
    fake = SimpleNamespace(
        all_patterns=(
            _pattern("ivs-bad", "Você vai perder 10 kg em 30 dias: {topic}"),
            _pattern("ivs-good", "Uma pergunta responsável sobre {topic} para refletir"),
        )
    )
    request = _request()
    before = deepcopy(request.model_dump())
    hooks = generate_deterministic(request, fake)
    assert len(hooks) == 1
    assert hooks[0].pattern_id == "ivs-good"
    assert hooks[0].compliance.status is ComplianceStatus.PASS
    assert request.model_dump() == before


def test_pipeline_discards_claim_introduced_by_context():
    fake = SimpleNamespace(
        all_patterns=(
            _pattern("ivs-context", "Um contexto para avaliar: {context}"),
            _pattern("ivs-safe", "Uma pergunta responsável sobre {topic} para refletir"),
        )
    )
    hooks = generate_deterministic(
        _request(context="Você vai perder 10 kg em 30 dias"),
        fake,
    )
    assert hooks[0].pattern_id == "ivs-safe"


def test_pipeline_discards_claim_introduced_by_required_words():
    fake = SimpleNamespace(
        all_patterns=(_pattern("ivs-required", "Uma pergunta sobre {topic} para refletir"),)
    )
    with pytest.raises(ValueError, match=r"generated=0.*blocked=12"):
        generate_deterministic(
            _request(required_words=["Você vai perder 10 kg em 30 dias"]),
            fake,
        )


def test_pipeline_keeps_review_visible():
    fake = SimpleNamespace(
        all_patterns=(_pattern("ivs-review", "Este método reduz 37% da gordura: {topic}"),)
    )
    hook = generate_deterministic(_request(), fake)[0]
    assert hook.compliance.status is ComplianceStatus.REVIEW
    assert hook.compliance.reasons == ["UNSOURCED_CLINICAL_NUMBER"]


def test_pipeline_reports_blocked_capacity_without_sensitive_text():
    fake = SimpleNamespace(
        all_patterns=(_pattern("ivs-bad", "Você vai perder 10 kg em 30 dias: {topic}"),)
    )
    with pytest.raises(ValueError) as captured:
        generate_deterministic(_request(count=2), fake)
    message = str(captured.value)
    assert "requested=2" in message and "generated=0" in message and "blocked=12" in message
    assert "perder" not in message


def test_pipeline_universal_remains_pass_with_fake_library():
    fake = SimpleNamespace(
        all_patterns=(
            _pattern("universal-test", "Você vai perder 10 kg em 30 dias: {topic}", "universal"),
        )
    )
    hook = generate_deterministic(_request(library="universal"), fake)[0]
    assert hook.compliance.status is ComplianceStatus.PASS


def test_all_rendered_ivs_templates_are_clear_in_existing_scenarios(rules):
    scenarios = (
        {
            "topic": "sono",
            "audience": "mulheres adultas",
            "desired_outcome": "escolhas conscientes",
            "context": "na rotina",
            "required_word": "fonte",
        },
        {
            "topic": "alimentação",
            "audience": "pessoas cuidadosas",
            "desired_outcome": "decisões melhores",
            "context": "no cotidiano",
            "required_word": "critério",
        },
        {
            "topic": "fontes confiáveis",
            "audience": "profissionais atentos",
            "desired_outcome": "leituras responsáveis",
            "context": "na revisão",
            "required_word": "evidência",
        },
    )
    for pattern in rules.patterns("ivs-health"):
        for values in scenarios:
            result = evaluate_compliance(pattern.template.format(**values), "ivs-health", rules)
            assert result.status is ComplianceStatus.PASS, (pattern.id, result)
