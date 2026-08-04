from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
from types import SimpleNamespace

import pytest

from hook_intelligence.domain.models import GenerationRequest
from hook_intelligence.engine.composer import (
    CandidateConstraintError,
    PatternCompositionError,
    compose_pattern,
    contains_forbidden,
)
from hook_intelligence.engine.library import HookLibrary, Pattern
from hook_intelligence.engine.pipeline import generate_deterministic
from hook_intelligence.engine.selector import select_patterns, stable_rank


def request(**overrides):
    values = {
        "topic": "qualidade do sono",
        "channel": "reel",
        "objective": "retention",
        "audience": "mulheres acima de 40",
        "count": 12,
    }
    values.update(overrides)
    return GenerationRequest(**values)


def pattern(
    pattern_id="universal-test-01",
    *,
    template="Um olhar cuidadoso sobre {topic} para {audience}",
    library="universal",
    mechanism="curiosity_gap",
    objectives=("retention",),
    channels=("reel",),
    awareness=("problem_aware",),
    tones=("premium",),
    intensity=1,
):
    slots = tuple(
        slot
        for slot in ("topic", "audience", "desired_outcome", "context", "required_word")
        if "{" + slot + "}" in template
    )
    return Pattern(
        pattern_id,
        library,
        mechanism,
        objectives,
        channels,
        awareness,
        tones,
        template,
        slots,
        "Explicação editorial segura e suficiente para o teste unitário.",
        intensity,
    )


def test_generates_requested_unique_hooks_for_combination_without_exact_dataset_match():
    hooks = generate_deterministic(request())

    assert isinstance(hooks, tuple)
    assert len(hooks) == 12
    assert len({hook.text.casefold() for hook in hooks}) == 12


def test_required_and_forbidden_words_are_enforced():
    hooks = generate_deterministic(
        request(
            topic="energia",
            channel="carousel",
            objective="education",
            audience="empreendedores",
            required_words=["rotina"],
            forbidden_words=["milagre"],
            count=8,
        )
    )

    assert len(hooks) == 8
    assert all("rotina" in hook.text.casefold() for hook in hooks)
    assert all("milagre" not in hook.text.casefold() for hook in hooks)


def test_repeated_request_has_identical_content_order_and_ids():
    generation_request = request()
    first = generate_deterministic(generation_request)
    second = generate_deterministic(generation_request)

    assert [(hook.text, hook.pattern_id, hook.id) for hook in first] == [
        (hook.text, hook.pattern_id, hook.id) for hook in second
    ]


def test_stable_rank_is_exact_sha256_and_hard_filters_are_applied():
    assert (
        stable_rank("tema público", "pattern-1")
        == sha256("tema público:pattern-1".encode()).hexdigest()
    )
    patterns = (
        pattern("keep", library="ivs-health", mechanism="authority", intensity=1),
        pattern("wrong-library", mechanism="authority", intensity=1),
        pattern("wrong-mechanism", library="ivs-health", intensity=1),
        pattern("too-intense", library="ivs-health", mechanism="authority", intensity=3),
    )
    library = SimpleNamespace(all_patterns=patterns)
    selected = select_patterns(
        request(library="ivs-health", mechanism="authority", intensity=2), library
    )

    assert selected == (patterns[0],)


def test_empty_hard_pool_has_contextual_error():
    library = SimpleNamespace(all_patterns=(pattern(intensity=3),))
    with pytest.raises(ValueError, match=r"library=universal.*intensity=1"):
        select_patterns(request(intensity=1), library)


def test_preferences_rank_exact_first_then_use_stable_fallback():
    exact = pattern("exact")
    objective_only = pattern("objective", channels=("email",))
    channel_only = pattern("channel", objectives=("education",))
    neither = pattern("neither", channels=("email",), objectives=("education",))
    library = SimpleNamespace(all_patterns=(neither, channel_only, objective_only, exact))

    selected = select_patterns(request(), library)

    assert selected[0] is exact
    assert selected.index(objective_only) < selected.index(channel_only)
    assert selected[-1] is neither
    assert set(selected) == set(library.all_patterns)


def test_count_fifty_uses_deterministic_editorial_variations():
    hooks = generate_deterministic(request(count=50, max_length=100))

    assert len(hooks) == 50
    assert len({hook.text.casefold() for hook in hooks}) == 50
    assert max(len(hook.text) for hook in hooks) <= 100
    assert any(not hook.text.endswith((".", "!", "?")) for hook in hooks)


def test_composer_revalidates_slots_and_treats_values_as_literal_data():
    bad = pattern(template="Entenda {unknown_slot} com segurança")
    with pytest.raises(ValueError, match="unknown_slot"):
        compose_pattern(bad, request(), 0)

    injected = compose_pattern(
        pattern(template="Um ponto sobre {topic} para analisar com cuidado"),
        request(topic="sono {unknown_slot}\nsem pressa"),
        0,
    )
    assert "{unknown_slot}" in injected
    assert "\n" not in injected


def test_max_length_never_cuts_words_and_preserves_required_words():
    generation_request = request(
        topic="planejamento de energia sustentável no trabalho",
        required_words=["rotina consciente"],
        max_length=55,
    )
    with pytest.raises(CandidateConstraintError, match="integralmente.*max_length"):
        compose_pattern(
            pattern(template="Uma análise ampla de {topic} para escolhas mais consistentes"),
            generation_request,
            0,
        )
    with pytest.raises(CandidateConstraintError, match="required_words.*max_length"):
        compose_pattern(
            pattern(template="Veja {topic}"),
            request(required_words=["x" * 40], max_length=30),
            0,
        )


def test_forbidden_matching_is_unicode_casefolded_and_expression_bounded():
    assert contains_forbidden("Evite o MILAGRE agora", ["milagre"])
    assert contains_forbidden("Use STRASSE com cuidado", ["Straße"])
    assert contains_forbidden("Uma rotina de alto impacto", ["alto impacto"])
    assert not contains_forbidden("Uma ideia milagreira", ["milagre"])
    assert contains_forbidden("Atenção ao cafe\u0301", ["café"])
    assert contains_forbidden("Use ＭＩＬＡＧＲＥ agora", ["milagre"])

    with pytest.raises(ValueError, match="forbidden"):
        compose_pattern(
            pattern(template="Milagre em {topic} para todas as pessoas"),
            request(forbidden_words=["milagre"]),
            0,
        )


def test_pipeline_skips_forbidden_templates_and_does_not_mutate_inputs():
    bad = pattern("bad", template="Milagre em {topic} para analisar")
    good = pattern("good", template="Critérios sobre {topic} para analisar")
    library = SimpleNamespace(all_patterns=(bad, good))
    generation_request = request(forbidden_words=["milagre"], count=2)
    request_before = deepcopy(generation_request.model_dump())
    patterns_before = library.all_patterns

    hooks = generate_deterministic(generation_request, library)

    assert len(hooks) == 2
    assert all(hook.pattern_id == "good" for hook in hooks)
    assert generation_request.model_dump() == request_before
    assert library.all_patterns == patterns_before


def test_hook_metadata_is_complete_and_valid():
    hook = generate_deterministic(request(count=1))[0]

    assert hook.mechanisms
    assert hook.source.value == "deterministic"
    assert hook.engine_version
    assert hook.explanation
    assert hook.compliance.status.value == "pass"
    assert hook.compliance.reasons == []
    assert hook.created_at.utcoffset() is not None
    assert 0 <= hook.scores.overall <= 100


def test_pipeline_reports_requested_and_generated_when_capacity_is_impossible():
    only = pattern(template="Milagre em {topic} para analisar")
    library = SimpleNamespace(all_patterns=(only,))
    with pytest.raises(ValueError, match=r"requested=2.*generated=0"):
        generate_deterministic(request(forbidden_words=["milagre"], count=2), library)


def test_real_library_is_not_mutated():
    library = HookLibrary.load_default()
    before = library.all_patterns
    generate_deterministic(request(count=2), library)
    assert library.all_patterns == before


def test_request_is_strictly_revalidated_after_model_copy():
    invalid_updates = (
        {"topic": None},
        {"required_words": None},
        {"forbidden_words": None},
        {"max_length": "100"},
        {"topic": " \t "},
        {"audience": "\n "},
        {"required_words": ["ok", " "]},
        {"forbidden_words": [""]},
    )
    for update in invalid_updates:
        corrupted = request().model_copy(update=update)
        with pytest.raises(ValueError, match="GenerationRequest|request|vazi"):
            generate_deterministic(corrupted)


def test_request_normalization_deduplicates_and_detects_canonical_contradiction():
    original = request(required_words=[" café ", "cafe\u0301", "ＣＡＦÉ"], count=1)
    hook = generate_deterministic(original)[0]
    assert hook.text.casefold().count("café") == 1
    assert original.required_words == [" café ", "cafe\u0301", "ＣＡＦÉ"]

    contradictory = request(required_words=["cafe\u0301"], forbidden_words=[" CAFÉ "])
    with pytest.raises(ValueError, match="contradição.*café"):
        generate_deterministic(contradictory)


def test_canonical_requests_have_same_content_and_ids():
    first = generate_deterministic(request(topic="café produtivo", count=3))
    second = generate_deterministic(request(topic="ｃａｆｅ\u0301   produtivo", count=3))
    assert [(item.text, item.id) for item in first] == [(item.text, item.id) for item in second]


def test_nfkc_dedupe_skips_compatibility_equivalent_candidates():
    normal = pattern("normal", template="Foco em {topic} para decisões melhores")
    fullwidth = pattern("fullwidth", template="Ｆｏｃｏ em {topic} para decisões melhores")
    library = SimpleNamespace(all_patterns=(normal, fullwidth))
    hooks = generate_deterministic(request(count=2), library)
    assert len(hooks) == 2
    assert hooks[0].pattern_id == hooks[1].pattern_id


@pytest.mark.parametrize(
    "template, declared",
    (
        ("Entenda {topic", ("topic",)),
        ("Entenda {topic:>10}", ("topic",)),
        ("Entenda {topic!r}", ("topic",)),
        ("Entenda {unknown}", ("unknown",)),
        ("Entenda {topic} e {topic}", ("topic", "topic")),
        ("Entenda {topic}", ("audience",)),
    ),
)
def test_pipeline_propagates_structural_pattern_errors(template, declared):
    broken = replace(pattern("broken", template=template), slots=declared)
    library = SimpleNamespace(all_patterns=(broken,))
    with pytest.raises(PatternCompositionError, match="pattern_id=broken"):
        generate_deterministic(request(count=1), library)


def test_pipeline_only_skips_candidate_constraint_errors():
    forbidden = pattern("forbidden", template="Milagre em {topic} para analisar")
    good = pattern("good", template="Uma reflexão sobre {topic} para analisar melhor")
    hooks = generate_deterministic(
        request(forbidden_words=["milagre"], count=1),
        SimpleNamespace(all_patterns=(forbidden, good)),
    )
    assert hooks[0].pattern_id == "good"


def test_composer_rejects_dangling_portuguese_endings_without_truncating():
    for ending in (
        "de",
        "do",
        "da",
        "para",
        "com",
        "sem",
        "e",
        "ou",
        "que",
        "quando",
        "no",
        "na",
        "ao",
        "o",
        "uma",
    ):
        dangling = pattern(
            f"dangling-{ending}", template=f"Uma ideia completa sobre {{topic}} {ending}"
        )
        with pytest.raises(CandidateConstraintError, match="final pendente"):
            compose_pattern(dangling, request(), 0)
