from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import ClassVar

from evaligator.core.models import ScoreResult, ScoreType


class BaseScorer(ABC):
    """Convenience base for the built-in scorers.

    Subclasses override ``name``/``score_type``/``threshold`` as class attributes and
    implement :meth:`score`. Anything that satisfies :class:`~evaligator.core.protocols.Scorer`
    is accepted by the framework, so this class is optional.
    """

    name: ClassVar[str] = "base"
    score_type: ClassVar[ScoreType] = ScoreType.NUMERIC
    threshold: ClassVar[float] = 0.5

    @abstractmethod
    def score(self, output: str, expected: str | None = None) -> ScoreResult: ...

    def score_batch(
        self,
        outputs: Sequence[str],
        expecteds: Sequence[str | None] | None = None,
    ) -> list[ScoreResult]:
        if expecteds is None:
            expecteds = [None] * len(outputs)
        if len(outputs) != len(expecteds):
            raise ValueError("outputs and expecteds must have the same length")
        return [
            self.score(output, expected)
            for output, expected in zip(outputs, expecteds, strict=True)
        ]

    def _result(self, score: float, *, reason: str = "", raw_value: object = None) -> ScoreResult:
        return ScoreResult(
            name=self.name,
            score=score,
            passed=score >= self.threshold,
            reason=reason,
            raw_value=raw_value,
        )
