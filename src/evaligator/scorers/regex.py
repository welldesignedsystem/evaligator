from __future__ import annotations

import re
from typing import ClassVar

from evaligator.core.errors import ScorerError
from evaligator.core.models import ScoreResult, ScoreType
from evaligator.scorers.base import BaseScorer


class RegexMatch(BaseScorer):
    """Passes when the configured regular expression is found in the output.

    The pattern is a fixed criterion supplied at construction; the ``expected``
    argument of :meth:`score` is ignored.
    """

    name: ClassVar[str] = "regex_match"
    score_type: ClassVar[ScoreType] = ScoreType.BINARY
    threshold: ClassVar[float] = 1.0

    def __init__(self, pattern: str) -> None:
        try:
            self._pattern = re.compile(pattern)
        except re.error as exc:
            raise ScorerError(f"invalid regex {pattern!r}: {exc}") from exc
        self.pattern = pattern

    def score(self, output: str, expected: str | None = None) -> ScoreResult:
        matched = self._pattern.search(output) is not None
        return self._result(
            1.0 if matched else 0.0,
            reason=(
                f"output matches /{self.pattern}/"
                if matched
                else f"output does not match /{self.pattern}/"
            ),
            raw_value={"output": output, "pattern": self.pattern},
        )
