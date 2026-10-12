from __future__ import annotations

import pytest

from evaligator.core.protocols import Scorer
from evaligator.scorers.exact import ExactMatch
from tests.contract.scorer_contract import ScorerContract


class TestExactMatchContract(ScorerContract):
    @pytest.fixture
    def scorers(self) -> list[Scorer]:
        return [ExactMatch()]

    @pytest.fixture
    def samples(self) -> list[tuple[str, str | None]]:
        return [("paris", "paris"), ("paris", "london"), ("anything", None), ("", "")]
