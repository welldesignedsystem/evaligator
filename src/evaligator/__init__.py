from evaligator.core.dataset import Dataset
from evaligator.core.models import EvalCase, EvalReport, EvalResult, ScoreResult, ScoreType
from evaligator.core.protocols import Scorer
from evaligator.scorers.base import BaseScorer
from evaligator.scorers.exact import ExactMatch

__all__ = [
    "BaseScorer",
    "Dataset",
    "EvalCase",
    "EvalReport",
    "EvalResult",
    "ExactMatch",
    "ScoreResult",
    "ScoreType",
    "Scorer",
]


def main() -> None:
    print("Hello from evaligator!")
