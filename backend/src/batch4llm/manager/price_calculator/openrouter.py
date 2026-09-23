import logging
import re

import requests

from batch4llm.manager.price_calculator.pricing_provider import PricingProvider

logger = logging.getLogger(__name__)

_MODELS_URL = "https://openrouter.ai/api/v1/models"

# Anthropic's own model list includes dated snapshot ids (e.g.
# "claude-opus-4-5-20251101") that OpenRouter doesn't price separately from
# the unversioned id ("claude-opus-4-5" / "claude-opus-4.5").
_SNAPSHOT_DATE_RE = re.compile(r"-\d{8}$")


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

        base_model = _SNAPSHOT_DATE_RE.sub("", model)

        for candidate_model in dict.fromkeys((model, base_model)):
            model_id = f"{provider}/{candidate_model}"
            if model_id in self._cache:
                return self._cache[model_id]

        raise ValueError(
            f"Model '{provider}/{model}' not found in OpenRouter pricing data"
        )

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

        raw_prices: dict[str, tuple[float, float]] = {}
        for entry in models:
            model_id = entry.get("id")
            pricing = entry.get("pricing") or {}
            try:
                input_per_m = float(pricing.get("prompt", 0)) * 1_000_000
                output_per_m = float(pricing.get("completion", 0)) * 1_000_000
            except (ValueError, TypeError):
                continue
            raw_prices[model_id] = (input_per_m, output_per_m)

        result: dict[str, tuple[float, float]] = {}
        for entry in models:
            model_id = entry.get("id")
            if model_id not in raw_prices:
                continue

            # A "~"-prefixed "always latest" alias's own listed price can lag
            # behind the model it currently points to (observed for
            # deepseek-flash-latest: alias listed $0.12/$0.48 while its
            # target, deepseek-v4.1-flash, priced at $0.15/$0.60) — prefer
            # the target's price when OpenRouter names one.
            target_slug = (entry.get("alias_target") or {}).get("slug")
            price = raw_prices.get(target_slug) or raw_prices[model_id]

            result[model_id] = price
            for alias in self._aliases_for(model_id):
                result.setdefault(alias, price)

        return result

    @staticmethod
    def _aliases_for(model_id: str) -> set[str]:
        """Alternate spellings a provider's own model list might use for the
        same OpenRouter entry:
        - "~google/gemini-pro-latest" (OpenRouter's "always latest" alias
          marker) vs. "google/gemini-pro-latest"
        - "~deepseek/deepseek-flash-latest" vs. DeepSeek's own shorthand
          "deepseek-flash" (no "-latest" suffix) — every "~"-prefixed entry
          currently observed on OpenRouter ends in "-latest"
        - "anthropic/claude-opus-4.5" vs. Anthropic's own "claude-opus-4-5"
        """
        clean_id = model_id.removeprefix("~")
        candidates = {model_id, clean_id}
        if clean_id.endswith("-latest"):
            candidates.add(clean_id.removesuffix("-latest"))

        aliases = set()
        for candidate in candidates:
            aliases.add(candidate)
            aliases.add(candidate.replace(".", "-"))
        aliases.discard(model_id)
        return aliases
