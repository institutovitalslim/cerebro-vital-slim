from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.content_radar import (
    BaselineObservation,
    MetricSelection,
    build_baseline,
    classify_signal,
    normalize_format,
    select_metric,
)


NOW = datetime(2026, 7, 29, 12, 0, tzinfo=timezone.utc)


def obs(
    idx: int,
    value: float,
    *,
    profile: str = "dra.camilapaes",
    network: str = "instagram",
    content_format: str = "reel",
    metric_basis: str = "public_interactions",
    source_kind: str = "approved",
    source_active: bool = True,
) -> BaselineObservation:
    return BaselineObservation(
        content_item_id=f"item-{idx}",
        external_id=f"external-{idx}",
        source_network=network,
        source_profile=profile,
        canonical_format=content_format,
        metric_basis=metric_basis,
        metric_value=value,
        observed_at=NOW - timedelta(hours=idx),
        published_at=NOW - timedelta(hours=idx, days=2),
        source_kind=source_kind,
        source_active=source_active,
        url=f"https://example.com/{idx}",
    )


def test_missing_metrics_never_become_estimated_views() -> None:
    selected = select_metric({"likes": 100, "comments": 12})

    assert selected == MetricSelection(
        basis="public_interactions",
        value=112,
        components={"likes": 100, "comments": 12},
    )
    assert selected.basis != "views"


def test_absent_metrics_stay_absent_instead_of_zero() -> None:
    assert select_metric({}) is None
    assert select_metric({"views": None, "likes": None, "comments": None}) is None


def test_explicit_zero_is_observed_but_not_fabricated() -> None:
    selected = select_metric({"views": 0})

    assert selected == MetricSelection(basis="views", value=0, components={"views": 0})


def test_real_views_take_precedence_over_public_interactions() -> None:
    selected = select_metric({"views": 4_200, "likes": 80, "comments": 9})

    assert selected == MetricSelection(basis="views", value=4_200, components={"views": 4_200})


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("clips", "reel"),
        ("reels", "reel"),
        ("reel", "reel"),
        ("carousel_container", "carousel"),
        ("carrossel", "carousel"),
        ("feed", "post"),
        ("post", "post"),
        ("stories", "story"),
        (None, "other"),
    ],
)
def test_format_is_normalized_at_the_boundary(raw: str | None, expected: str) -> None:
    assert normalize_format(raw) == expected


def test_nine_comparable_items_are_insufficient() -> None:
    baseline = build_baseline(obs(99, 100), [obs(i, i + 1) for i in range(9)])

    assert baseline.maturity == "insufficient"
    assert baseline.sample_count == 9
    assert baseline.median_value is None
    assert baseline.performance_ratio is None
    assert baseline.signal_state == "insufficient"


def test_ten_items_form_a_provisional_median() -> None:
    baseline = build_baseline(obs(99, 30), [obs(i, value) for i, value in enumerate(range(1, 11))])

    assert baseline.maturity == "provisional"
    assert baseline.sample_count == 10
    assert baseline.median_value == pytest.approx(5.5)
    assert baseline.performance_ratio == pytest.approx(30 / 5.5)
    assert baseline.signal_state == "outlier"


def test_twenty_items_form_a_target_median() -> None:
    baseline = build_baseline(obs(99, 200), [obs(i, value) for i, value in enumerate(range(1, 21))])

    assert baseline.maturity == "target"
    assert baseline.sample_count == 20
    assert baseline.median_value == pytest.approx(10.5)
    assert baseline.signal_state == "breakout"


def test_only_thirty_most_recent_items_are_used() -> None:
    controls = [obs(i, i + 1) for i in range(35)]
    baseline = build_baseline(obs(99, 100), controls)

    assert baseline.sample_count == 30
    assert {member.content_item_id for member in baseline.members} == {f"item-{i}" for i in range(30)}


def test_candidate_is_never_part_of_its_own_baseline() -> None:
    candidate = obs(5, 100)
    controls = [obs(i, 10) for i in range(12)]
    baseline = build_baseline(candidate, controls)

    assert all(member.content_item_id != candidate.content_item_id for member in baseline.members)


def test_baseline_never_mixes_profile_format_network_or_basis() -> None:
    candidate = obs(99, 100)
    controls = [obs(i, 10) for i in range(10)]
    controls += [obs(20, 999, profile="outra.pessoa")]
    controls += [obs(21, 999, content_format="carousel")]
    controls += [obs(22, 999, network="youtube")]
    controls += [obs(23, 999, metric_basis="views")]

    baseline = build_baseline(candidate, controls)

    assert baseline.sample_count == 10
    assert baseline.median_value == 10


def test_excluded_and_unresolved_thematic_sources_do_not_enter_baseline() -> None:
    candidate = obs(99, 100)
    controls = [obs(i, 10) for i in range(10)]
    controls += [obs(20, 999, source_kind="excluded")]
    controls += [obs(21, 999, source_kind="thematic_search")]

    baseline = build_baseline(candidate, controls)

    assert baseline.sample_count == 10
    assert baseline.median_value == 10


def test_inactive_sources_never_enter_or_receive_an_eligible_baseline() -> None:
    candidate = obs(99, 100)
    controls = [obs(i, 10) for i in range(10)]
    controls.append(obs(20, 999, source_active=False))

    baseline = build_baseline(candidate, controls)

    assert baseline.sample_count == 10
    assert baseline.median_value == 10

    inactive_candidate = build_baseline(obs(100, 100, source_active=False), controls)
    assert inactive_candidate.signal_state == "insufficient"
    assert inactive_candidate.reason == "source_not_active"


def test_zero_median_does_not_create_infinity_or_fake_signal() -> None:
    candidate = obs(99, 100)
    baseline = build_baseline(candidate, [obs(i, 0) for i in range(10)])

    assert baseline.median_value == 0
    assert baseline.performance_ratio is None
    assert baseline.signal_state == "insufficient"
    assert baseline.reason == "zero_baseline"


def test_median_resists_one_extreme_outlier() -> None:
    controls = [obs(i, value) for i, value in enumerate([10] * 9 + [1_000_000])]
    baseline = build_baseline(obs(99, 35), controls)

    assert baseline.median_value == 10
    assert baseline.performance_ratio == 3.5
    assert baseline.signal_state == "outlier"


def test_comparison_posts_are_three_controls_closest_to_the_median() -> None:
    controls = [obs(i, value) for i, value in enumerate([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])]
    baseline = build_baseline(obs(99, 40), controls)

    assert len(baseline.comparison_posts) == 3
    assert [post.metric_value for post in baseline.comparison_posts] == [5, 6, 4]


@pytest.mark.parametrize(
    ("multiple", "expected"),
    [
        (None, "insufficient"),
        (1.0, "signal"),
        (2.99, "signal"),
        (3.0, "outlier"),
        (9.99, "outlier"),
        (10.0, "breakout"),
    ],
)
def test_signal_thresholds_are_explicit(multiple: float | None, expected: str) -> None:
    assert classify_signal(multiple) == expected
