from __future__ import annotations

import pytest

from evaligator.core.errors import ScorerError
from evaligator.core.models import ScoreType
from evaligator.scorers.regex import RegexMatch


def test_regex_passes_when_pattern_matches_output() -> None:
    result = RegexMatch(r"\d{3}").score("order 123 confirmed")
    assert result.score == 1.0
    assert result.passed is True
    assert result.name == "regex_match"


def test_regex_fails_when_pattern_does_not_match() -> None:
    result = RegexMatch(r"\d{3}").score("no digits here")
    assert result.score == 0.0
    assert result.passed is False


def test_regex_uses_search_not_fullmatch() -> None:
    assert RegexMatch(r"paris").score("the capital is paris!").passed is True


def test_regex_ignores_expected_argument() -> None:
    scorer = RegexMatch(r"\d+")
    assert scorer.score("v2", "totally-different").score == 1.0


def test_regex_invalid_pattern_raises_scorer_error() -> None:
    with pytest.raises(ScorerError):
        RegexMatch("(")


def test_regex_score_type_is_binary() -> None:
    assert RegexMatch.score_type is ScoreType.BINARY
