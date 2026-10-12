from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field

from evaligator.core.dataset import Dataset
from evaligator.core.models import EvalCase, EvalReport, EvalResult, ScoreResult
from evaligator.core.protocols import Scorer

type SystemUnderTest = Callable[[str], str]


@dataclass
class Runner:
    """The basic evaluation loop.

    Calls the system under test on each case, applies every scorer, and decides
    a case passes when the share of scorers that passed is at least
    ``pass_threshold`` (default: all of them).
    """

    system: SystemUnderTest
    scorers: list[Scorer] = field(default_factory=list)
    pass_threshold: float = 1.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.pass_threshold <= 1.0:
            raise ValueError(f"pass_threshold must be between 0 and 1, got {self.pass_threshold}")

    def run_case(self, case: EvalCase) -> EvalResult:
        start = time.perf_counter()
        try:
            output = self.system(case.input)
        except Exception as exc:
            return EvalResult(
                case=case,
                output="",
                passed=False,
                error=f"{type(exc).__name__}: {exc}",
                latency_ms=_elapsed_ms(start),
            )

        scores: list[ScoreResult] = []
        error: str | None = None
        try:
            for scorer in self.scorers:
                scores.append(scorer.score(output, case.expected))
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"

        return EvalResult(
            case=case,
            output=output,
            scores=scores,
            passed=error is None and self._passes(scores),
            error=error,
            latency_ms=_elapsed_ms(start),
        )

    def run(self, dataset: Dataset) -> EvalReport:
        return EvalReport(name=dataset.name, results=[self.run_case(case) for case in dataset])

    def _passes(self, scores: list[ScoreResult]) -> bool:
        if not scores:
            return False
        fraction = sum(1 for score in scores if score.passed) / len(scores)
        return fraction >= self.pass_threshold


def _elapsed_ms(start: float) -> float:
    return (time.perf_counter() - start) * 1000.0
