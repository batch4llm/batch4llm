from typing import Optional, List
from pydantic import BaseModel, Field


class PriceCalculationRequest(BaseModel):
    provider: str = Field(..., min_length=3, max_length=70)
    model: str = Field(..., min_length=3, max_length=70)
    file_reader: str
    file_ids: List[int]
    prompt: Optional[str] = Field(None, max_length=5000)
    output: Optional[str] = Field(None, max_length=5000)
