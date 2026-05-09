import requests
import tiktoken

from batch4llm.manager.file_reader.reader_manager import FileReaderManager


def estimate_batch_costs_in_usd(
    provider: str,
    model: str,
    file_paths: list[str],
    file_reader: str,
    prompt: str = None,
    output: str = None,
):

    input_cost_per_1m, output_cost_per_1m = get_price_per_token(provider, model)

    run_prompt_tokens = token_count(model, prompt) * len(file_paths) if prompt else 0
    run_output_tokens = token_count(model, output) * len(file_paths) if output else 0

    file_tokens = 0
    for file_path in file_paths:
        file_tokens += tokens_from_file(file_path, file_reader, model)

    return ((input_cost_per_1m / 1_000_000) * (run_prompt_tokens + file_tokens)) + (
        (output_cost_per_1m / 1_000_000) * run_output_tokens
    )


def calculate_price(
    input_tokens: int, output_tokens: int, provider: str, model: str
) -> float:
    input_cost_per_1m, output_cost_per_1m = get_price_per_token(provider, model)
    return (input_cost_per_1m / 1_000_000) * input_tokens + (
        output_cost_per_1m / 1_000_000
    ) * output_tokens


def get_price_per_token(provider: str, model: str) -> tuple[float, float]:
    params = {"provider": provider, "model": model}
    r = requests.get("https://www.helicone.ai/api/llm-costs", params=params)
    result = r.json()

    try:
        input_cost_per_1m = result["data"][0]["input_cost_per_1m"]
        output_cost_per_1m = result["data"][0]["output_cost_per_1m"]
    except IndexError:
        raise ValueError(f"Model '{model}' not found with the provider '{provider}'.")
    return input_cost_per_1m, output_cost_per_1m


def tokens_from_file(file_path: str, file_reader, model) -> int:
    content = FileReaderManager.read(file_reader, file_path)
    return token_count(model, content)


def token_count(model: str, text: str) -> int:
    try:
        enc = tiktoken.encoding_for_model(model)
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))
