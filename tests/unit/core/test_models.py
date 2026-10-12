from __future__ import annotations

from evaligator.core.models import EvalCase, EvalReport, EvalResult, ScoreResult


def _result(*, passed: bool, latency_ms: float = 0.0) -> EvalResult:
    return EvalResult(
        case=EvalCase(input="q"),
        output="a",
        scores=[ScoreResult(name="exact_match", score=1.0 if passed else 0.0, passed=passed)],
        passed=passed,
        latency_ms=latency_ms,
    )


def test_empty_report_has_zeroed_aggregates() -> None:
    report = EvalReport(name="empty")
    assert (report.total, report.passed, report.failed) == (0, 0, 0)
    assert report.pass_rate == 0.0
    assert report.avg_scores == {}
    assert report.avg_latency_ms == 0.0


def test_report_aggregates_counts_and_rates() -> None:
    report = EvalReport(name="run", results=[_result(passed=True), _result(passed=False)])
    assert (report.total, report.passed, report.failed) == (2, 1, 1)
    assert report.pass_rate == 0.5


def test_report_averages_scores_and_latency() -> None:
    results = [
        _result(passed=True, latency_ms=10.0),
        _result(passed=False, latency_ms=30.0),
    ]
    report = EvalReport(name="run", results=results)
    assert report.avg_scores == {"exact_match": 0.5}
    assert report.avg_latency_ms == 20.0


def test_report_summary_mentions_counts_and_scores() -> None:
    report = EvalReport(name="run", results=[_result(passed=True)])
    summary = report.summary()
    assert "run" in summary
    assert "Cases: 1" in summary
    assert "exact_match" in summary


def test_eval_case_defaults() -> None:
    case = EvalCase(input="q")
    assert case.expected is None
    assert case.metadata == {}
    assert case.tags == []
