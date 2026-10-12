from __future__ import annotations

from collections.abc import Sequence

import pytest

from evaligator.core.models import ScoreType
from evaligator.core.protocols import Scorer


class ScorerContract:
    """Behavioural contract every :class:`Scorer` implementation must satisfy.

    Subclass it (name the subclass ``Test...`` so pytest collects it) and provide the
    ``scorers`` and ``samples`` fixtures. Keeping this suite in one place is what makes
    adding scorers and adapters safe.
    """

    @pytest.fixture
    def scorers(self) -> Sequence[Scorer]:
        raise NotImplementedError

    @pytest.fixture
    def samples(self) -> Sequence[tuple[str, str | None]]:
        raise NotImplementedError

    def test_satisfies_scorer_protocol(
        self, scorers: Sequence[Scorer], samples: Sequence[tuple[str, str | None]]
    ) -> None:
        for scorer in scorers:
            assert isinstance(scorer, Scorer)
            assert scorer.name
            assert isinstance(scorer.score_type, ScoreType)
            assert isinstance(scorer.threshold, float)

    def test_score_returns_consistent_result(
        self, scorers: Sequence[Scorer], samples: Sequence[tuple[str, str | None]]
    ) -> None:
        for scorer in scorers:
            for output, expected in samples:
                result = scorer.score(output, expected)
                assert result.name == scorer.name
                assert 0.0 <= result.score <= 1.0
                assert result.passed == (result.score >= scorer.threshold)

    def test_score_batch_mirrors_score(
        self, scorers: Sequence[Scorer], samples: Sequence[tuple[str, str | None]]
    ) -> None:
        outputs = [output for output, _ in samples]
        expecteds = [expected for _, expected in samples]
        for scorer in scorers:
            batched = scorer.score_batch(outputs, expecteds)
            singles = [scorer.score(output, expected) for output, expected in samples]
            assert [(r.name, r.score, r.passed) for r in batched] == [
                (r.name, r.score, r.passed) for r in singles
            ]
