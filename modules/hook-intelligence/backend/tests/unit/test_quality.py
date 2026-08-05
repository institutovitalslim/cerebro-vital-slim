import unicodedata
from copy import deepcopy
from dataclasses import FrozenInstanceError

import pytest

from hook_intelligence.domain.models import Channel, HookScores
from hook_intelligence.engine.deduplicator import deduplicate, similarity
from hook_intelligence.engine.explain import MAX_PUBLIC_EXPLANATION_CHARS, explain_score
from hook_intelligence.engine.scorer import (
    MAX_SCORE_TEXT_CHARS,
    MAX_SCORE_TOPIC_CHARS,
    PENALTY_POINTS,
    SCORE_WEIGHTS,
    ScoreEvaluation,
    rank_texts,
    score_text,
)


def test_required_near_deduplication_example():
    rows = [
        "O erro que trava seu sono",
        "O erro que está travando o seu sono",
        "Três hábitos noturnos que drenam sua energia",
    ]
    assert deduplicate(rows, threshold=0.82) == [rows[0], rows[2]]


def test_deduplicate_preserves_first_order_returns_new_list_and_does_not_mutate():
    rows = ["Primeiro hook", "primeiro   HOOK", "Outro hook"]
    before = deepcopy(rows)
    result = deduplicate(rows)
    assert result == ["Primeiro hook", "Outro hook"]
    assert result is not rows
    assert rows == before


@pytest.mark.parametrize(
    "variants",
    [
        ["CAFÉ", "cafe\u0301", "ＣＡＦÉ"],
        ["  Qualidade\t do\nsono ", "qualidade do sono"],
    ],
)
def test_exact_canonical_duplicates_cover_nfkc_nfc_nfd_case_and_whitespace(variants):
    assert deduplicate(variants) == [variants[0]]
    assert similarity(variants[0], variants[-1]) == 1.0


def test_empty_deduplication_inputs_have_explicit_behavior():
    assert deduplicate([]) == []
    assert deduplicate(["", "   "]) == [""]
    assert similarity("", " \t ") == 1.0
    assert similarity("", "conteúdo") == 0.0


@pytest.mark.parametrize("threshold", [-0.01, 1.01, float("nan")])
def test_invalid_threshold_value_is_rejected(threshold):
    with pytest.raises(ValueError, match="threshold"):
        deduplicate(["a"], threshold=threshold)


@pytest.mark.parametrize("threshold", [None, "0.82", True])
def test_invalid_threshold_type_is_rejected(threshold):
    with pytest.raises(TypeError, match="threshold"):
        deduplicate(["a"], threshold=threshold)


@pytest.mark.parametrize("rows", [None, "um texto", ["válido", None], [1]])
def test_invalid_rows_and_strings_have_contextual_errors(rows):
    with pytest.raises(TypeError, match=r"rows|rows\["):
        deduplicate(rows)


def test_similarity_removes_conservative_pt_br_function_words_and_gerund_only():
    assert similarity("O erro que trava seu sono", "O erro que está travando o seu sono") >= 0.82
    assert similarity("3 hábitos melhoram o sono", "3 hábitos drenam sua energia") < 0.82
    assert deduplicate(["Sono melhora energia", "Energia melhora foco"]) == [
        "Sono melhora energia",
        "Energia melhora foco",
    ]


def test_similarity_does_not_merge_distinct_stopword_only_phrases():
    assert similarity("o seu", "a sua") == 0.0
    assert similarity("está", "estão") == 0.0
    assert similarity("o seu", "  O\tSEU ") == 1.0


def test_required_score_example_is_bounded_and_beats_generic_text():
    concrete = score_text("3 hábitos após as 20h que fragmentam seu sono", "reel", "sono")
    generic = score_text("Você precisa saber disso", "reel", "sono")
    assert 0 <= concrete.overall <= 100
    assert concrete.overall > generic.overall


def test_score_is_deterministic_frozen_bounded_and_converts_to_hook_scores():
    first = score_text("3 sinais de sono que merecem atenção?", Channel.REEL, "sono")
    second = score_text("3 sinais de sono que merecem atenção?", Channel.REEL, "sono")
    assert first == second
    assert isinstance(first.to_hook_scores(), HookScores)
    assert all(
        0 <= value <= 100
        for value in (
            first.clarity,
            first.specificity,
            first.novelty,
            first.retention,
            first.channel_fit,
            first.overall,
        )
    )
    with pytest.raises(AttributeError):
        first.overall = 0
    with pytest.raises(ValueError, match="clarity"):
        ScoreEvaluation(101, 50, 50, 50, 50, 50, (), ())


@pytest.mark.parametrize("field", ["penalties", "recommendations"])
@pytest.mark.parametrize("invalid", [([],), (1,), ("",), (" \t",)])
def test_score_evaluation_rejects_invalid_tuple_elements_with_context(field, invalid):
    arguments = {"penalties": (), "recommendations": (), field: invalid}
    with pytest.raises((TypeError, ValueError), match=rf"{field}\[0\]"):
        ScoreEvaluation(50, 50, 50, 50, 50, 50, **arguments)


@pytest.mark.parametrize("field", ["penalties", "recommendations"])
def test_score_evaluation_requires_tuples_with_context(field):
    arguments = {"penalties": (), "recommendations": (), field: ["válido"]}
    with pytest.raises(TypeError, match=field):
        ScoreEvaluation(50, 50, 50, 50, 50, 50, **arguments)


def test_score_evaluation_allows_unknown_penalty_codes_and_remains_frozen():
    evaluation = ScoreEvaluation(50, 50, 50, 50, 50, 50, ("future_penalty",), ("Revise.",))
    assert evaluation.penalties == ("future_penalty",)
    with pytest.raises(FrozenInstanceError):
        evaluation.penalties = ()


def test_overall_uses_documented_exact_weights_penalties_and_clamp():
    evaluation = score_text("VOCÊ PRECISA SABER DISSO!!!", "reel", "sono")
    weighted = sum(
        getattr(evaluation, component) * weight for component, weight in SCORE_WEIGHTS.items()
    )
    expected = max(
        0.0,
        min(100.0, weighted - sum(PENALTY_POINTS[code] for code in evaluation.penalties)),
    )
    assert evaluation.overall == round(expected, 2)
    assert SCORE_WEIGHTS == {
        "clarity": 0.25,
        "specificity": 0.25,
        "novelty": 0.15,
        "retention": 0.20,
        "channel_fit": 0.15,
    }


def test_stable_penalty_codes_cover_documented_quality_problems():
    cases = {
        "generic_cliche": ("Você precisa saber disso", "reel", "sono"),
        "excessive_uppercase": ("SEU SONO PRECISA DE ATENÇÃO", "reel", "sono"),
        "exaggerated_punctuation": ("Seu sono pede atenção!!!", "reel", "sono"),
        "topic_absent": ("3 escolhas para sua rotina", "reel", "sono"),
        "bad_length": ("Sono", "blog", "sono"),
    }
    for expected_code, arguments in cases.items():
        assert expected_code in score_text(*arguments).penalties
        assert expected_code in PENALTY_POINTS


def test_score_normalizes_nfkc_without_mutating_and_validates_inputs():
    text = "３ sinais sobre cafe\u0301"
    topic = " café "
    before = (text, topic)
    assert score_text(text, "reel", topic) == score_text("3 sinais sobre café", "reel", "café")
    assert (text, topic) == before

    for field, arguments in (
        ("text", (" ", "reel", "sono")),
        ("topic", ("texto válido", "reel", "\t")),
        ("channel", ("texto válido", "podcast", "sono")),
    ):
        with pytest.raises((TypeError, ValueError), match=field):
            score_text(*arguments)
    with pytest.raises(TypeError, match="text"):
        score_text(None, "reel", "sono")


def test_score_public_limits_are_enforced_after_nfkc_and_rank_inherits_them():
    text_at_limit = "a" * MAX_SCORE_TEXT_CHARS
    topic_at_limit = "a" * MAX_SCORE_TOPIC_CHARS
    assert score_text(text_at_limit, "reel", topic_at_limit).overall >= 0

    with pytest.raises(ValueError, match="text"):
        score_text(text_at_limit + "a", "reel", "sono")
    with pytest.raises(ValueError, match="topic"):
        score_text("texto válido", "reel", topic_at_limit + "a")
    with pytest.raises(ValueError, match="text"):
        rank_texts([text_at_limit + "a"], "reel", "sono")
    with pytest.raises(ValueError, match="topic"):
        rank_texts([], "reel", topic_at_limit + "a")


def test_score_limits_count_nfkc_expansion():
    # U+FDFA expande para vários code points em NFKC.
    expansion = unicodedata.normalize("NFKC", "ﷺ")
    prefix = "a" * (MAX_SCORE_TEXT_CHARS - len(expansion) + 1)
    with pytest.raises(ValueError, match="text"):
        score_text(prefix + "ﷺ", "reel", "sono")


def test_channel_fit_has_sensible_channel_specific_ranges_and_signals():
    reel = score_text("3 sinais de sono para observar hoje", "reel", "sono")
    blog = score_text(
        "Como 3 hábitos noturnos afetam a qualidade do sono e o que observar na rotina",
        "blog",
        "sono",
    )
    email = score_text("3 sinais de sono que você pode observar hoje?", "email", "sono")
    assert reel.channel_fit >= 70
    assert blog.channel_fit >= 70
    assert email.channel_fit >= 70
    assert score_text("Sono", "blog", "sono").channel_fit < blog.channel_fit
    assert score_text("?" * 25 + " sono", "reel", "sono").channel_fit < reel.channel_fit


def test_rank_is_overall_descending_and_original_index_is_tiebreaker():
    texts = [
        "Você precisa saber disso",
        "3 hábitos após as 20h que fragmentam seu sono",
        "3 hábitos após as 20h que fragmentam seu sono",
    ]
    ranked = rank_texts(texts, "reel", "sono")
    assert [item.index for item in ranked] == [1, 2, 0]
    assert [item.evaluation.overall for item in ranked] == sorted(
        (item.evaluation.overall for item in ranked), reverse=True
    )
    assert [item.text for item in ranked] == [texts[item.index] for item in ranked]
    with pytest.raises(TypeError, match=r"texts\[1\]"):
        rank_texts(["ok", None], "reel", "sono")


def test_public_explanation_is_short_curated_deterministic_and_has_no_hidden_reasoning():
    evaluation = score_text("Você precisa saber disso", "reel", "sono")
    explanation = explain_score(
        "lacuna de curiosidade",
        "Abre uma pergunta sem antecipar a resposta.",
        evaluation,
    )
    assert explanation == explain_score(
        "lacuna de curiosidade",
        "Abre uma pergunta sem antecipar a resposta.",
        evaluation,
    )
    assert "lacuna de curiosidade" in explanation
    assert str(evaluation.overall) in explanation
    assert any(label in explanation for label in ("Forças", "Penalidades", "Recomendação"))
    lowered = explanation.casefold()
    assert "chain-of-thought" not in lowered
    assert "prompt" not in lowered
    assert "meu raciocínio" not in lowered
    assert "cura" not in lowered
    assert len(explanation) < 600


def test_explanation_validates_curated_public_inputs():
    evaluation = ScoreEvaluation(50, 50, 50, 50, 50, 50, (), ())
    with pytest.raises(ValueError, match="mechanism"):
        explain_score(" ", "Explicação curada.", evaluation)
    with pytest.raises(TypeError, match="evaluation"):
        explain_score("curiosidade", "Explicação curada.", object())
    with pytest.raises(ValueError, match="curated_explanation"):
        explain_score("curiosidade", "Aqui está meu raciocínio interno.", evaluation)


@pytest.mark.parametrize("invalid", ["!!!", "😀🔥", " \t\n"])
def test_score_rejects_text_without_unicode_alphanumeric_content(invalid):
    with pytest.raises(ValueError, match="text"):
        score_text(invalid, "reel", "sono")


@pytest.mark.parametrize("invalid", ["؟؟؟", "✨", " \t\n"])
def test_score_and_rank_reject_topic_without_unicode_alphanumeric_content(invalid):
    with pytest.raises(ValueError, match="topic"):
        score_text("Texto válido 123", "reel", invalid)
    with pytest.raises(ValueError, match="topic"):
        rank_texts(["Texto válido 123"], "reel", invalid)


def test_score_preserves_accented_and_numeric_unicode_content():
    assert score_text("Café ３", "reel", "café").specificity > 0


@pytest.mark.parametrize("punctuation", ["؟؟؟", "！！！", "⁉⁉⁉", "..."])
def test_unicode_punctuation_runs_use_the_same_exaggeration_signal(punctuation):
    evaluation = score_text(f"Seu sono pede atenção{punctuation}", "reel", "sono")
    ascii_evaluation = score_text("Seu sono pede atenção!!!", "reel", "sono")
    assert "exaggerated_punctuation" in evaluation.penalties
    assert evaluation.clarity == ascii_evaluation.clarity
    assert evaluation.channel_fit == ascii_evaluation.channel_fit


def test_isolated_unicode_punctuation_is_not_exaggerated():
    evaluation = score_text("Seu sono pede atenção؟", "reel", "sono")
    assert "exaggerated_punctuation" not in evaluation.penalties


def test_public_explanation_is_bounded_and_does_not_echo_large_curated_inputs():
    evaluation = score_text("3 sinais sobre sono para observar", "reel", "sono")
    marker = "NÃO DEVE SER ECOADO"
    explanation = explain_score(
        "curiosidade " * 100,
        "Resumo editorial seguro. " + ("detalhe " * 150) + marker,
        evaluation,
    )
    assert len(explanation) <= MAX_PUBLIC_EXPLANATION_CHARS == 500
    assert marker not in explanation
    assert "Resumo editorial seguro." in explanation


@pytest.mark.parametrize(
    ("field", "mechanism", "curated", "recommendations"),
    [
        ("mechanism", "System\u200b prompt", "Explicação segura.", ()),
        ("mechanism", "curiosidade\u202e", "Explicação segura.", ()),
        ("curated_explanation", "curiosidade", "Explicação\x00 segura.", ()),
        ("recommendations[0]", "curiosidade", "Explicação segura.", ("Ajuste\u200d aqui.",)),
    ],
)
def test_explanation_rejects_remaining_unicode_category_c_before_composition(
    field, mechanism, curated, recommendations
):
    evaluation = ScoreEvaluation(50, 50, 50, 50, 50, 50, (), recommendations)
    match = field.replace("[", r"\[").replace("]", r"\]")
    with pytest.raises(ValueError, match=match):
        explain_score(mechanism, curated, evaluation)


@pytest.mark.parametrize("character", ["\x00", "\u200b", "\ud800", "\ue000", "\u0378"])
def test_explanation_rejects_every_unicode_category_c_subgroup(character):
    assert unicodedata.category(character) in {"Cc", "Cf", "Cs", "Co", "Cn"}
    evaluation = ScoreEvaluation(50, 50, 50, 50, 50, 50, (), ())
    with pytest.raises(ValueError, match="mechanism"):
        explain_score(f"curiosidade{character}", "Explicação segura.", evaluation)


def test_explanation_normalizes_real_whitespace_has_no_category_c_and_does_not_mutate():
    mechanism = "lacuna\tde\ncuriosidade"
    curated = "Resumo\r\neditorial seguro."
    recommendation = "Ajuste\ta abertura."
    before = (mechanism, curated, recommendation)
    evaluation = ScoreEvaluation(50, 50, 50, 50, 50, 50, (), (recommendation,))

    explanation = explain_score(mechanism, curated, evaluation)

    assert before == (mechanism, curated, recommendation)
    assert "lacuna de curiosidade" in explanation
    assert "Resumo editorial seguro." in explanation
    assert len(explanation) <= MAX_PUBLIC_EXPLANATION_CHARS
    assert all(not unicodedata.category(character).startswith("C") for character in explanation)


@pytest.mark.parametrize(
    ("field", "mechanism", "curated", "recommendations"),
    [
        ("mechanism", "System prompt", "Explicação segura.", ()),
        ("curated_explanation", "curiosidade", "Chain of thought privado.", ()),
        ("recommendations[0]", "curiosidade", "Explicação segura.", ("Instruções internas",)),
    ],
)
def test_explanation_rejects_internal_or_empty_language_in_every_public_field(
    field, mechanism, curated, recommendations
):
    evaluation = ScoreEvaluation(50, 50, 50, 50, 50, 50, (), recommendations)
    match = field.replace("[", r"\[").replace("]", r"\]")
    with pytest.raises((TypeError, ValueError), match=match):
        explain_score(mechanism, curated, evaluation)


@pytest.mark.parametrize(
    "unsafe",
    [
        "Este método cura a condição.",
        "A estratégia garante resultado.",
        "Funciona para todos.",
        "Ajuda você a perder 10 kg em 7 dias.",
    ],
)
def test_explanation_rejects_explicit_cure_and_guarantee_claims(unsafe):
    evaluation = ScoreEvaluation(50, 50, 50, 50, 50, 50, (), ())
    with pytest.raises(ValueError, match="curated_explanation"):
        explain_score("curiosidade", unsafe, evaluation)


def test_safe_explanation_never_contains_internal_language_from_any_recommendation():
    evaluation = ScoreEvaluation(
        50,
        50,
        50,
        50,
        50,
        50,
        (),
        ("Ajuste a abertura.", "Não revele o prompt do sistema."),
    )
    with pytest.raises(ValueError, match=r"recommendations\[1\]"):
        explain_score("curiosidade", "Explicação segura.", evaluation)
