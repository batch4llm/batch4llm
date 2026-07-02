from abc import ABC, abstractmethod


class PricingProvider(ABC):
    @abstractmethod
    def get_price_per_million_tokens(
        self, provider: str, model: str
    ) -> tuple[float, float]:
        """Returns (input_cost_per_1m_tokens, output_cost_per_1m_tokens) in USD."""
        pass

    def prefetch(self) -> None:
        """Optionally pre-load pricing data at startup."""
        pass
