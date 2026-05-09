from dataclasses import dataclass
from typing import Optional


@dataclass
class ProviderBatchStatus:
    is_complete: bool
    is_failed: bool
    completed_count: int
    failed_count: int
    raw_status: str


@dataclass
class BatchResultEntry:
    custom_id: str
    success: bool
    output: Optional[str]
    input_tokens: int
    output_tokens: int
    error_message: Optional[str]


@dataclass
class LLMClientResponse:
    client: str
    model: str
    prompt: str
    input: str
    output: str
    input_tokens: int
    output_tokens: int
    temperature: Optional[float]
    json_format: Optional[bool]
    top_p: Optional[float]
    top_k: Optional[int]
    max_output_tokens: Optional[int]
    seed: Optional[int]
    context_window: Optional[int]
