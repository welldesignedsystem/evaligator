from __future__ import annotations

from typing import ClassVar

from evaligator.core.models import ScoreResult, ScoreType
from evaligator.scorers.base import BaseScorer


class ExactMatch(BaseScorer):
    """Passes only when the output equals the expected answer exactly (1.0 or 0.0)."""

    name: ClassVar[str] = "exact_match"
    score_type: ClassVar[ScoreType] = ScoreType.BINARY
    threshold: ClassVar[float] = 1.0

    def score(self, output: str, expected: str | None = None) -> ScoreResult:
        matched = expected is not None and output == expected
        return self._result(
            1.0 if matched else 0.0,
            reason="output matches expected" if matched else "output does not match expected",
            raw_value={"output": output, "expected": expected},
        )
