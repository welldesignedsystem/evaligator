from __future__ import annotations

from typing import ClassVar

import pytest

from evaligator.core.dataset import Dataset
from evaligator.core.models import EvalCase, ScoreResult, ScoreType
from evaligator.runners.base import Runner
from evaligator.scorers.base import BaseScorer
from evaligator.scorers.exact import ExactMatch
from evaligator.scorers.regex import RegexMatch


class _BoomScorer(BaseScorer):
    name: ClassVar[str] = "boom"
    score_type: ClassVar[ScoreType] = ScoreType.BINARY
    threshold: ClassVar[float] = 1.0

    def score(self, output: str, expected: str | None = None) -> ScoreResult:
        raise RuntimeError("scorer exploded")


def _echo(text: str) -> str:
    return text


def test_run_case_scores_the_system_output() -> None:
    runner = Runner(system=_echo, scorers=[ExactMatch()])
    result = runner.run_case(EvalCase(input="a", expected="a"))
    assert result.output == "a"
    assert result.passed is True
    assert [score.name for score in result.scores] == ["exact_match"]
    assert result.latency_ms >= 0.0
    assert result.error is None


def test_default_threshold_requires_all_scorers_to_pass() -> None:
    runner = Runner(system=_echo, scorers=[ExactMatch(), RegexMatch(r"\d+")])
    result = runner.run_case(EvalCase(input="a", expected="a"))
    assert result.passed is False


def test_case_passes_when_share_of_scorers_meets_threshold() -> None:
    runner = Runner(system=_echo, scorers=[ExactMatch(), RegexMatch(r"\d+")], pass_threshold=0.5)
    assert runner.run_case(EvalCase(input="a", expected="a")).passed is True


def test_case_fails_when_share_of_scorers_below_threshold() -> None:
    runner = Runner(system=_echo, scorers=[ExactMatch(), RegexMatch(r"\d+")], pass_threshold=0.75)
    assert runner.run_case(EvalCase(input="a", expected="a")).passed is False


def test_case_fails_when_there_are_no_scorers() -> None:
    runner = Runner(system=_echo, scorers=[])
    assert runner.run_case(EvalCase(input="a", expected="a")).passed is False


def test_system_exception_is_captured() -> None:
    def boom(_: str) -> str:
        raise ValueError("system failed")

    result = Runner(system=boom, scorers=[ExactMatch()]).run_case(EvalCase(input="a"))
    assert result.passed is False
    assert result.output == ""
    assert result.scores == []
    assert result.error is not None
    assert "ValueError" in result.error


def test_scorer_exception_is_captured_and_keeps_partial_scores() -> None:
    runner = Runner(system=_echo, scorers=[ExactMatch(), _BoomScorer()])
    result = runner.run_case(EvalCase(input="a", expected="a"))
    assert result.passed is False
    assert [score.name for score in result.scores] == ["exact_match"]
    assert result.error is not None
    assert "RuntimeError" in result.error


def test_run_aggregates_results_into_a_report() -> None:
    dataset = Dataset(
        name="demo",
        cases=[EvalCase(input="a", expected="a"), EvalCase(input="b", expected="c")],
    )
    report = Runner(system=_echo, scorers=[ExactMatch()]).run(dataset)
    assert report.name == "demo"
    assert (report.total, report.passed, report.failed) == (2, 1, 1)
    assert report.pass_rate == 0.5
    assert report.avg_scores == {"exact_match": 0.5}


def test_pass_threshold_must_be_a_fraction() -> None:
    with pytest.raises(ValueError):
        Runner(system=_echo, pass_threshold=1.5)
    with pytest.raises(ValueError):
        Runner(system=_echo, pass_threshold=-0.1)
