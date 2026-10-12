from __future__ import annotations

from evaligator.core.models import ScoreType
from evaligator.scorers.exact import ExactMatch


def test_exact_match_scores_one_on_identical_strings() -> None:
    result = ExactMatch().score("paris", "paris")
    assert result.score == 1.0
    assert result.passed is True
    assert result.name == "exact_match"


def test_exact_match_scores_zero_on_different_strings() -> None:
    result = ExactMatch().score("paris", "london")
    assert result.score == 0.0
    assert result.passed is False
    assert result.reason


def test_exact_match_fails_when_expected_missing() -> None:
    result = ExactMatch().score("paris", None)
    assert result.score == 0.0
    assert result.passed is False


def test_exact_match_score_type_is_binary() -> None:
    assert ExactMatch.score_type is ScoreType.BINARY


def test_exact_match_batch_uses_default_loop() -> None:
    results = ExactMatch().score_batch(["a", "b"], ["a", "c"])
    assert [result.passed for result in results] == [True, False]
