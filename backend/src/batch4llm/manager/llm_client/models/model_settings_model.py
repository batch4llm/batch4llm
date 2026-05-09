from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelSettings:
    temperature: Optional[float] = None
    json_format: Optional[bool] = False
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    max_output_tokens: Optional[int] = None
    seed: Optional[int] = None
