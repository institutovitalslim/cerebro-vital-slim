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


@pytest.mark.parametrize(
    "text",
    [
        "Não tome 2 cápsulas por dia.",
        "Não compre agora ou será tarde demais.",
        "Não existe resultado garantido para todas as pessoas.",
        "Não é a única solução que funciona.",
        "Nunca tome 2 cápsulas por dia!",
        "Aviso, jamais compre agora ou será tarde demais.",
        "ＮÃＯ ＴＯＭＥ 2 cápsulas por dia.",
    ],
)
def test_negated_clauses_are_masked_conservatively(rules, text):
    assert evaluate_compliance(text, "ivs-health", rules).status is ComplianceStatus.PASS


@pytest.mark.parametrize(
    ("text", "reason"),
    [
        ("Não não tome 2 cápsulas por dia.", "DIRECT_PRESCRIPTION"),
        ("Não nunca tome 2 cápsulas por dia.", "DIRECT_PRESCRIPTION"),
        ("Nunca jamais este protocolo cura a diabetes.", "CURE_CLAIM"),
    ],
)
def test_double_negation_does_not_hide_positive_claim(rules, text, reason):
    before = text

    result = evaluate_compliance(text, "ivs-health", rules)

    assert result.status is ComplianceStatus.BLOCK
    assert result.reasons == [reason]
    assert text == before


def test_negation_with_exception_word_does_not_hide_positive_claim(rules):
    result = evaluate_compliance(
        "Não apenas este protocolo cura a diabetes.",
        "ivs-health",
        rules,
    )
    assert result.status is ComplianceStatus.BLOCK
    assert result.reasons == ["CURE_CLAIM"]


def test_negated_clause_over_300_chars_is_scanned_conservatively(rules):
    text = "Não " + ("contexto " * 38) + "este protocolo cura a diabetes"
    assert len(text.strip()) > 300

    result = evaluate_compliance(text, "ivs-health", rules)

    assert result.status is ComplianceStatus.BLOCK
    assert result.reasons == ["CURE_CLAIM"]


@pytest.mark.parametrize(
    "text",
    [
        "A frase Tome 2 cápsulas por dia é um exemplo proibido.",
        "A frase Tome 2 cápsulas, por dia é um exemplo proibido.",
        "O texto Cure a obesidade definitivamente é inadequado.",
        "A expressão COMPRE AGORA OU SERÁ TARDE DEMAIS seria um exemplo do que evitar.",
        "Ｏ ＥＸＥＭＰＬＯ Cure a obesidade definitivamente é proibido.",
    ],
)
def test_explicit_metalinguistic_examples_are_masked(rules, text):
    assert evaluate_compliance(text, "ivs-health", rules).status is ComplianceStatus.PASS


@pytest.mark.parametrize("punctuation", [".", "!", "?", ";", ":", "。", "！", "？", ","])
def test_positive_claim_after_any_unicode_punctuation_is_not_masked(rules, punctuation):
    text = f"Não existe cura{punctuation}Este protocolo cura a diabetes."
    result = evaluate_compliance(text, "ivs-health", rules)
    assert result.status is ComplianceStatus.BLOCK
    assert result.reasons == ["CURE_CLAIM"]


@pytest.mark.parametrize(
    "text",
    [
        "NÃO APENAS este protocolo cura a diabetes.",
        "ＮÃＯ ＳＯＭＥＮＴＥ este protocolo cura a diabetes.",
        "Jamais só este protocolo cura a diabetes.",
    ],
)
def test_negation_exception_words_are_case_and_width_insensitive(rules, text):
    result = evaluate_compliance(text, "ivs-health", rules)
    assert result.status is ComplianceStatus.BLOCK
    assert result.reasons == ["CURE_CLAIM"]


def test_metalinguistic_example_over_300_chars_returns_to_claim_scan(rules):
    text = "A frase Tome 2 cápsulas por dia " + ("contexto " * 34) + "é um exemplo proibido."
    assert len(text.removesuffix(".")) > 300

    result = evaluate_compliance(text, "ivs-health", rules)

    assert result.status is ComplianceStatus.BLOCK
    assert result.reasons == ["DIRECT_PRESCRIPTION"]


def test_metalinguistic_marker_without_safe_suffix_is_scanned(rules):
    result = evaluate_compliance(
        "A frase Tome 2 cápsulas por dia aparece no roteiro.",
        "ivs-health",
        rules,
    )
    assert result.status is ComplianceStatus.BLOCK
    assert result.reasons == ["DIRECT_PRESCRIPTION"]


def test_unicode_masking_does_not_mutate_original_input(rules):
    text = "Não existe cura。A frase Tome 2 cápsulas, por dia é um exemplo proibido."
    before = text

    evaluate_compliance(text, "ivs-health", rules)

    assert text == before


@pytest.mark.parametrize(
    ("text", "reasons"),
    [
        ("Não espere, tome 2 cápsulas por dia.", ["DIRECT_PRESCRIPTION"]),
        ("Não existe cura. Este protocolo cura a diabetes.", ["CURE_CLAIM"]),
        (
            (
                "A frase Tome 2 cápsulas por dia é um exemplo proibido. "
                "Este protocolo cura a diabetes."
            ),
            ["CURE_CLAIM"],
        ),
        (
            (
                "O texto Cure a obesidade definitivamente é inadequado; "
                "compre agora ou será tarde demais."
            ),
            ["FALSE_URGENCY"],
        ),
    ],
)
def test_masking_does_not_hide_positive_claims_in_new_clauses(rules, text, reasons):
    result = evaluate_compliance(text, "ivs-health", rules)
    assert result.status is ComplianceStatus.BLOCK
    assert result.reasons == reasons


@pytest.mark.parametrize(
    "text",
    [
        "Este protocolo curou a diabetes.",
        "Este protocolo curará a diabetes.",
        "Esse método CURA a obesidade.",
        "Este tratamento pode curar a depressão.",
    ],
)
def test_contextual_cure_conjugations_are_blocked(rules, text):
    result = evaluate_compliance(text, "ivs-health", rules)
    assert result.status is ComplianceStatus.BLOCK
    assert result.reasons == ["CURE_CLAIM"]


@pytest.mark.parametrize("text", ["Voce tem diabetes.", "Seu diagnostico é câncer."])
def test_diagnosis_accepts_explicit_unaccented_variants(rules, text):
    result = evaluate_compliance(text, "ivs-health", rules)
    assert result.status is ComplianceStatus.BLOCK
    assert result.reasons == ["DIRECT_DIAGNOSIS"]


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


def test_universal_rejects_invalid_rules_library_before_early_pass():
    with pytest.raises(ValueError, match="rules_library.*HookLibrary"):
        evaluate_compliance("texto válido", Library.UNIVERSAL, object())  # type: ignore[arg-type]


def test_universal_with_valid_rules_library_does_not_scan(rules, monkeypatch):
    def fail_if_scanned(_text):
        pytest.fail("universal não deve executar scanner médico")

    monkeypatch.setattr(rules, "scan_forbidden_claims", fail_if_scanned)
    result = evaluate_compliance("texto válido", Library.UNIVERSAL, rules)
    assert result.status is ComplianceStatus.PASS
    assert result.reasons == []


def test_scanner_timeout_is_wrapped_without_engine_details():
    secret = "SECRET_RULE_AND_ENGINE_DETAIL"

    class TimeoutHookLibrary(HookLibrary):
        def scan_forbidden_claims(self, text):
            del text
            raise TimeoutError(secret)

    timeout_rules = TimeoutHookLibrary.load_default()

    with pytest.raises(ValueError) as captured:
        evaluate_compliance("Tome 2 cápsulas por dia.", "ivs-health", timeout_rules)

    assert str(captured.value) == "falha contextual ao avaliar regras médicas IVS"
    assert secret not in str(captured.value)
    assert captured.value.__cause__ is None
    assert captured.value.__suppress_context__ is True


def test_arbitrary_scanner_programming_error_is_not_swallowed(rules, monkeypatch):
    def fail_with_programming_error(_text):
        raise RuntimeError("programming bug")

    monkeypatch.setattr(rules, "scan_forbidden_claims", fail_with_programming_error)

    with pytest.raises(RuntimeError, match="programming bug"):
        evaluate_compliance("texto válido", "ivs-health", rules)


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


def test_masked_and_positive_claim_reasons_keep_dataset_order(rules):
    text = (
        "Não tome 2 cápsulas por dia. Este método reduz 37% da gordura. "
        "Voce tem diabetes. Este protocolo curou a diabetes. "
        "Resultado garantido para todas as pessoas."
    )
    result = evaluate_compliance(text, "ivs-health", rules)
    assert result.status is ComplianceStatus.BLOCK
    assert result.reasons == [
        "CURE_CLAIM",
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
