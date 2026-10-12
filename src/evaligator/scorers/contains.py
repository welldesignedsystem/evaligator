from __future__ import annotations

from typing import ClassVar

from evaligator.core.models import ScoreResult, ScoreType
from evaligator.scorers.base import BaseScorer


class Contains(BaseScorer):
    """Passes when the expected answer appears as a substring of the output."""

    name: ClassVar[str] = "contains"
    score_type: ClassVar[ScoreType] = ScoreType.BINARY
    threshold: ClassVar[float] = 1.0

    def score(self, output: str, expected: str | None = None) -> ScoreResult:
        matched = expected is not None and expected != "" and expected in output
        return self._result(
            1.0 if matched else 0.0,
            reason=(
                f"output contains {expected!r}"
                if matched
                else f"output does not contain {expected!r}"
            ),
            raw_value={"output": output, "expected": expected},
        )
