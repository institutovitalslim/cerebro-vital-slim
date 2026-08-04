from copy import deepcopy

import pytest

from hook_intelligence.domain.models import Channel, HookScores
from hook_intelligence.engine.deduplicator import deduplicate, similarity
from hook_intelligence.engine.explain import explain_score
from hook_intelligence.engine.scorer import (
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
