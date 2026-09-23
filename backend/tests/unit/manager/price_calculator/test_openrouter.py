from unittest.mock import patch

from batch4llm.manager.price_calculator.openrouter import OpenRouterPricingProvider

# A trimmed slice of real ids/pricing observed on https://openrouter.ai/api/v1/models,
# covering each naming mismatch this provider has to paper over.
_OPENROUTER_RESPONSE = {
    "data": [
        {
            "id": "anthropic/claude-opus-4.5",
            "pricing": {"prompt": "0.000005", "completion": "0.000025"},
        },
        {
            "id": "google/gemini-2.5-pro",
            "pricing": {"prompt": "0.00000125", "completion": "0.00001"},
        },
        {
            "id": "~google/gemini-pro-latest",
            "pricing": {"prompt": "0.000002", "completion": "0.000012"},
        },
        {
            "id": "mistralai/mistral-large",
            "pricing": {"prompt": "0.000002", "completion": "0.000006"},
        },
        {
            "id": "openai/gpt-4.1",
            "pricing": {"prompt": "0.000002", "completion": "0.000008"},
        },
        {
            "id": "~deepseek/deepseek-flash-latest",
            "pricing": {"prompt": "0.00000012", "completion": "0.00000048"},
            "alias_target": {"slug": "deepseek/deepseek-v4.1-flash"},
        },
        {
            "id": "deepseek/deepseek-v4.1-flash",
            "pricing": {"prompt": "0.00000015", "completion": "0.0000006"},
        },
    ]
}


def _provider():
    with patch(
        "batch4llm.manager.price_calculator.openrouter.requests.get"
    ) as mock_get:
        mock_get.return_value.json.return_value = _OPENROUTER_RESPONSE
        mock_get.return_value.raise_for_status.return_value = None
        provider = OpenRouterPricingProvider()
        provider.prefetch()
    return provider


def test_anthropic_dash_separated_version_matches_openrouter_dotted_id():
    provider = _provider()
    assert provider.get_price_per_million_tokens("anthropic", "claude-opus-4-5") == (
        5.0,
        25.0,
    )


def test_anthropic_dated_snapshot_falls_back_to_unversioned_id():
    provider = _provider()
    assert provider.get_price_per_million_tokens(
        "anthropic", "claude-opus-4-5-20251101"
    ) == (5.0, 25.0)


def test_gemini_model_matches_google_namespace():
    provider = _provider()
    assert provider.get_price_per_million_tokens("google", "gemini-2.5-pro") == (
        1.25,
        10.0,
    )


def test_gemini_latest_alias_matches_openrouters_tilde_prefixed_id():
    provider = _provider()
    assert provider.get_price_per_million_tokens("google", "gemini-pro-latest") == (
        2.0,
        12.0,
    )


def test_mistral_model_matches_mistralai_namespace():
    provider = _provider()
    assert provider.get_price_per_million_tokens("mistralai", "mistral-large") == (
        2.0,
        6.0,
    )


def test_provider_without_alias_matches_directly():
    provider = _provider()
    assert provider.get_price_per_million_tokens("openai", "gpt-4.1") == (2.0, 8.0)


def test_provider_shorthand_matches_openrouters_latest_alias_without_suffix():
    provider = _provider()
    assert provider.get_price_per_million_tokens("deepseek", "deepseek-flash") == (
        0.15,
        0.6,
    )


def test_stale_alias_pricing_is_overridden_by_its_alias_target():
    """OpenRouter's own top-level price for a "~"-alias can lag behind the
    model it currently points to; the alias_target's price should win."""
    provider = _provider()
    assert provider.get_price_per_million_tokens(
        "deepseek", "deepseek-flash-latest"
    ) == (0.15, 0.6)


def test_unknown_model_raises_value_error():
    provider = _provider()
    try:
        provider.get_price_per_million_tokens("openai", "does-not-exist")
        assert False, "expected ValueError"
    except ValueError as e:
        assert "not found in OpenRouter pricing data" in str(e)
