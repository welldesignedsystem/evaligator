"""Simple refund test, adapted from the DeepEval blog's "Install and First Test".

Scored by the local LiteLLM proxy judge (see zmot/setup/litellm) instead of a
direct OpenAI key.

The judge key and base URL come from the repo-root `.env` (`LITELLM_API_KEY`,
`LITELLM_API_BASE`). We load it by explicit path so the test works from any
working directory, not just the repo root.

Prereqs:
    cd zmot/setup/litellm && docker compose up -d

Run:
    uv run --with deepeval --with litellm \
        deepeval test run zmot/deepeval/test_refund.py
"""

import os
from pathlib import Path

from dotenv import load_dotenv

from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.models import LiteLLMModel
from deepeval.test_case import LLMTestCase, SingleTurnParams

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

judge = LiteLLMModel(
    # logical name exposed by the LiteLLM proxy (zmot/setup/litellm/config.yaml)
    model="litellm_proxy/nvidia/nemotron-3-super-120b-a12b:free",
    api_key=os.environ["LITELLM_API_KEY"],
    base_url=os.environ["LITELLM_API_BASE"],
    temperature=0,
)


def test_refund():
    correctness = GEval(
        name="Correctness",
        criteria="Determine if the 'actual output' is correct based on the 'expected output'.",
        evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT, SingleTurnParams.EXPECTED_OUTPUT],
        threshold=0.5,
        model=judge,
    )
    test_case = LLMTestCase(
        input="What if these shoes don't fit?",
        actual_output="You have 30 days to get a full refund at no extra cost.",
        expected_output="We offer a 30-day full refund at no extra costs but you have to return them in their original condition.",
    )
    assert_test(test_case, [correctness])
