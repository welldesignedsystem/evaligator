"""GEval: does the Python implementation match the algorithm described in markdown?

Compares the two artifacts:
    artifacts/01-algo-as-python.py   -> actual output (the implementation)
    artifacts/01-algo-in-markdown.md -> expected output (the spec)

Run:
    uv run --with deepeval --with litellm \
        deepeval test run zmot/deepeval/test_algorithm.py
"""

import os
from pathlib import Path

from dotenv import load_dotenv

from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.models import LiteLLMModel
from deepeval.test_case import LLMTestCase, SingleTurnParams

ARTIFACTS = Path(__file__).parent / "artifacts"
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

judge = LiteLLMModel(
    # logical name exposed by the LiteLLM proxy (zmot/setup/litellm/config.yaml)
    model="litellm_proxy/nvidia/nemotron-3-super-120b-a12b:free",
    api_key=os.environ["LITELLM_API_KEY"],
    base_url=os.environ["LITELLM_API_BASE"],
    temperature=0,
)


def test_algorithm_implementation_matches_spec():
    implementation = (ARTIFACTS / "01-algo-as-python.py").read_text()
    specification = (ARTIFACTS / "01-algo-in-markdown.md").read_text()

    correctness = GEval(
        name="Spec/implementation match",
        criteria=(
            "Determine if the Python implementation in the 'actual output' correctly "
            "implements the behaviour specified by the algorithm in the 'expected output' "
        ),
        evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT, SingleTurnParams.EXPECTED_OUTPUT],
        threshold=0.5,
        model=judge,
    )
    test_case = LLMTestCase(
        input="Implement an algorithm to return the K most frequent strings.",
        actual_output=implementation,
        expected_output=specification,
    )
    assert_test(test_case, [correctness])
