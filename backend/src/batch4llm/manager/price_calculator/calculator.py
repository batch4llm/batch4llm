import tiktoken

from batch4llm.manager.file_reader.reader_manager import FileReaderManager
from batch4llm.manager.price_calculator.openrouter import OpenRouterPricingProvider
from batch4llm.manager.price_calculator.pricing_provider import PricingProvider

_pricing_provider: PricingProvider = OpenRouterPricingProvider()

PROVIDER_BATCH_DISCOUNT = 0.5


def set_pricing_provider(provider: PricingProvider) -> None:
    global _pricing_provider
    _pricing_provider = provider


def prefetch_pricing() -> None:
    _pricing_provider.prefetch()


def estimate_batch_costs_in_usd(
    provider: str,
    model: str,
    file_paths: list[str],
    file_reader: str,
    prompt: str = None,
    output: str = None,
) -> float:
    input_cost_per_1m, output_cost_per_1m = (
        _pricing_provider.get_price_per_million_tokens(provider, model)
    )

    run_prompt_tokens = token_count(model, prompt) * len(file_paths) if prompt else 0
    run_output_tokens = token_count(model, output) * len(file_paths) if output else 0

    file_tokens = 0
    for file_path in file_paths:
        file_tokens += tokens_from_file(file_path, file_reader, model)

    return ((input_cost_per_1m / 1_000_000) * (run_prompt_tokens + file_tokens)) + (
        (output_cost_per_1m / 1_000_000) * run_output_tokens
    )


def get_model_pricing(provider: str, model: str) -> tuple[float, float] | None:
    """Returns (input_cost_per_1m_tokens, output_cost_per_1m_tokens), or None if unknown."""
    try:
        return _pricing_provider.get_price_per_million_tokens(provider, model)
    except ValueError:
        return None


def calculate_price(
    input_tokens: int,
    output_tokens: int,
    provider: str,
    model: str,
    is_provider_batch: bool = False,
) -> float:
    input_cost_per_1m, output_cost_per_1m = (
        _pricing_provider.get_price_per_million_tokens(provider, model)
    )
    price = (input_cost_per_1m / 1_000_000) * input_tokens + (
        output_cost_per_1m / 1_000_000
    ) * output_tokens
    if is_provider_batch:
        price *= PROVIDER_BATCH_DISCOUNT
    return price


def tokens_from_file(file_path: str, file_reader, model) -> int:
    content = FileReaderManager.read(file_reader, file_path)
    return token_count(model, content)


def token_count(model: str, text: str) -> int:
    try:
        enc = tiktoken.encoding_for_model(model)
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))
