from evaligator.core.dataset import Dataset
from evaligator.core.models import EvalCase, EvalReport, EvalResult, ScoreResult, ScoreType
from evaligator.core.protocols import Scorer
from evaligator.runners.base import Runner
from evaligator.scorers.base import BaseScorer
from evaligator.scorers.contains import Contains
from evaligator.scorers.exact import ExactMatch
from evaligator.scorers.regex import RegexMatch

__all__ = [
    "BaseScorer",
    "Contains",
    "Dataset",
    "EvalCase",
    "EvalReport",
    "EvalResult",
    "ExactMatch",
    "RegexMatch",
    "Runner",
    "ScoreResult",
    "ScoreType",
    "Scorer",
]


def main() -> None:
    print("Hello from evaligator!")
