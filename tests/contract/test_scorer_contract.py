from __future__ import annotations

import pytest

from evaligator.core.protocols import Scorer
from evaligator.scorers.contains import Contains
from evaligator.scorers.exact import ExactMatch
from evaligator.scorers.regex import RegexMatch
from tests.contract.scorer_contract import ScorerContract


class TestExactMatchContract(ScorerContract):
    @pytest.fixture
    def scorers(self) -> list[Scorer]:
        return [ExactMatch()]

    @pytest.fixture
    def samples(self) -> list[tuple[str, str | None]]:
        return [("paris", "paris"), ("paris", "london"), ("anything", None), ("", "")]


class TestContainsContract(ScorerContract):
    @pytest.fixture
    def scorers(self) -> list[Scorer]:
        return [Contains()]

    @pytest.fixture
    def samples(self) -> list[tuple[str, str | None]]:
        return [("the capital is paris", "paris"), ("paris", "london"), ("x", None), ("x", "")]


class TestRegexMatchContract(ScorerContract):
    @pytest.fixture
    def scorers(self) -> list[Scorer]:
        return [RegexMatch(r"\d+")]

    @pytest.fixture
    def samples(self) -> list[tuple[str, str | None]]:
        return [("v2", None), ("no digits", None), ("", None)]
