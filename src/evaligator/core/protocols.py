from __future__ import annotations

from collections.abc import Sequence
from typing import ClassVar, Protocol, runtime_checkable

from evaligator.core.models import ScoreResult, ScoreType


@runtime_checkable
class Scorer(Protocol):
    """Structural port every scorer satisfies.

    ``ClassVar`` because implementations declare ``name``/``score_type``/``threshold``
    as class-level overrides rather than instance state.
    """

    name: ClassVar[str]
    score_type: ClassVar[ScoreType]
    threshold: ClassVar[float]

    def score(self, output: str, expected: str | None = None) -> ScoreResult: ...

    def score_batch(
        self,
        outputs: Sequence[str],
        expecteds: Sequence[str | None] | None = None,
    ) -> list[ScoreResult]: ...
