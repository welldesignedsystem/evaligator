from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ScoreType(StrEnum):
    """The kind of value a scorer produces."""

    BINARY = "binary"
    NUMERIC = "numeric"
    LIKERT = "likert"
    CATEGORICAL = "categorical"


@dataclass(frozen=True, slots=True)
class EvalCase:
    """One test example: the input sent to the system under test plus context."""

    input: str
    expected: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class ScoreResult:
    """What a single scorer returns for a single output."""

    name: str
    score: float
    passed: bool
    reason: str = ""
    raw_value: Any = None


@dataclass(frozen=True, slots=True)
class EvalResult:
    """The outcome of running one :class:`EvalCase`."""

    case: EvalCase
    output: str
    scores: list[ScoreResult] = field(default_factory=list)
    passed: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
    latency_ms: float = 0.0
    error: str | None = None


def _mean_scores(results: list[EvalResult]) -> dict[str, float]:
    grouped: dict[str, list[float]] = {}
    for result in results:
        for score in result.scores:
            grouped.setdefault(score.name, []).append(score.score)
    return {name: sum(values) / len(values) for name, values in grouped.items()}


@dataclass
class EvalReport:
    """Aggregate of every :class:`EvalResult` for a run."""

    name: str
    results: list[EvalResult] = field(default_factory=list)
    total: int = field(init=False)
    passed: int = field(init=False)
    failed: int = field(init=False)
    pass_rate: float = field(init=False)
    avg_scores: dict[str, float] = field(init=False)
    avg_latency_ms: float = field(init=False)

    def __post_init__(self) -> None:
        self.total = len(self.results)
        self.passed = sum(1 for result in self.results if result.passed)
        self.failed = self.total - self.passed
        self.pass_rate = self.passed / self.total if self.total else 0.0
        self.avg_scores = _mean_scores(self.results)
        self.avg_latency_ms = (
            sum(result.latency_ms for result in self.results) / self.total if self.total else 0.0
        )

    def summary(self) -> str:
        lines = [
            f"Report: {self.name}",
            f"Cases: {self.total} | Passed: {self.passed} | Failed: {self.failed} "
            f"| Pass rate: {self.pass_rate:.1%}",
            f"Avg latency: {self.avg_latency_ms:.1f} ms",
        ]
        if self.avg_scores:
            lines.append("Average scores:")
            lines.extend(
                f"  {name}: {value:.3f}" for name, value in sorted(self.avg_scores.items())
            )
        return "\n".join(lines)
