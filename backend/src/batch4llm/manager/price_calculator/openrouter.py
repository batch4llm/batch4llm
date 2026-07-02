import logging

import requests

from batch4llm.manager.price_calculator.pricing_provider import PricingProvider

logger = logging.getLogger(__name__)

_MODELS_URL = "https://openrouter.ai/api/v1/models"


class OpenRouterPricingProvider(PricingProvider):

    def __init__(self):
        self._cache: dict[str, tuple[float, float]] | None = None

    def prefetch(self) -> None:
        self._cache = self._fetch()
        if not self._cache:
            logger.error(
                "OpenRouter returned no pricing data — cost calculation will not work"
            )

    def get_price_per_million_tokens(
        self, provider: str, model: str
    ) -> tuple[float, float]:
        if self._cache is None:
            self._cache = self._fetch()
        model_id = f"{provider}/{model}"
        if model_id not in self._cache:
            raise ValueError(f"Model '{model_id}' not found in OpenRouter pricing data")
        return self._cache[model_id]

    def _fetch(self) -> dict[str, tuple[float, float]]:
        try:
            r = requests.get(_MODELS_URL, timeout=10)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            logger.error(f"Failed to fetch OpenRouter pricing data: {e}")
            return {}

        models = data.get("data")
        if not models:
            logger.error("OpenRouter /api/v1/models returned empty response")
            return {}

        result: dict[str, tuple[float, float]] = {}
        for entry in models:
            model_id = entry.get("id")
            pricing = entry.get("pricing") or {}
            try:
                input_per_m = float(pricing.get("prompt", 0)) * 1_000_000
                output_per_m = float(pricing.get("completion", 0)) * 1_000_000
                result[model_id] = (input_per_m, output_per_m)
            except (ValueError, TypeError):
                continue

        return result
