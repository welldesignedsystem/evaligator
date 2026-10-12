from __future__ import annotations

from evaligator.core.models import ScoreType
from evaligator.scorers.contains import Contains


def test_contains_passes_when_expected_is_a_substring() -> None:
    result = Contains().score("the capital is paris", "paris")
    assert result.score == 1.0
    assert result.passed is True
    assert result.name == "contains"


def test_contains_fails_when_expected_is_absent() -> None:
    result = Contains().score("the capital is paris", "london")
    assert result.score == 0.0
    assert result.passed is False
    assert result.reason


def test_contains_is_case_sensitive_by_default() -> None:
    assert Contains().score("Paris", "paris").passed is False


def test_contains_fails_when_expected_is_none() -> None:
    result = Contains().score("anything", None)
    assert result.score == 0.0
    assert result.passed is False


def test_contains_fails_on_empty_expected() -> None:
    result = Contains().score("anything", "")
    assert result.score == 0.0
    assert result.passed is False


def test_contains_score_type_is_binary() -> None:
    assert Contains.score_type is ScoreType.BINARY
