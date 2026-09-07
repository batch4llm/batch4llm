"""Smoke tests against real LLM provider APIs.

Opt-in only: every test is marked `real_api` and skips itself when its
provider's API key isn't set. Run explicitly with:

    pytest backend/tests/integration -m real_api -v

Keep prompts and output caps small — these calls cost real money.
"""

import os

import pytest

from batch4llm.manager.llm_client.clients.anthropic_client import AnthropicLLMClient
from batch4llm.manager.llm_client.clients.gemini_client import GeminiLLMClient
from batch4llm.manager.llm_client.clients.openai_client import OpenAILLMClient
from batch4llm.manager.llm_client.models.model_settings_model import ModelSettings

PROMPT = "Reply with exactly one word: the capital of France."
CONTENT = "Answer now."

pytestmark = pytest.mark.real_api


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set"
)
def test_openai_real_call():
    client = OpenAILLMClient(api_token=os.environ["OPENAI_API_KEY"])
    model = os.environ.get("OPENAI_TEST_MODEL", "gpt-4o-mini")

    response = client.run(
        model=model,
        prompt=PROMPT,
        content=CONTENT,
        model_settings=ModelSettings(temperature=0, max_output_tokens=10),
    )

    assert response.output
    assert response.input_tokens > 0
    assert response.output_tokens > 0


@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY not set"
)
def test_anthropic_real_call():
    client = AnthropicLLMClient(api_token=os.environ["ANTHROPIC_API_KEY"])
    model = os.environ.get("ANTHROPIC_TEST_MODEL", "claude-haiku-4-5-20251001")

    response = client.run(
        model=model,
        prompt=PROMPT,
        content=CONTENT,
        model_settings=ModelSettings(temperature=0, max_output_tokens=10),
    )

    assert response.output
    assert response.input_tokens > 0
    assert response.output_tokens > 0


@pytest.mark.skipif(
    not os.environ.get("GEMINI_API_KEY"), reason="GEMINI_API_KEY not set"
)
def test_gemini_real_call():
    client = GeminiLLMClient(api_token=os.environ["GEMINI_API_KEY"])
    model = os.environ.get("GEMINI_TEST_MODEL", "gemini-2.5-flash")

    response = client.run(
        model=model,
        prompt=PROMPT,
        content=CONTENT,
        model_settings=ModelSettings(temperature=0, max_output_tokens=10),
    )

    assert response.output
    assert response.input_tokens > 0
    assert response.output_tokens > 0
