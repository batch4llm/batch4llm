from datetime import datetime
from pydantic import BaseModel


class ModelResponse(BaseModel):
    id: int
    endpoint_id: int
    endpoint_name: str
    provider: str
    model_name: str
    input_cost_per_1m_tokens: float | None
    output_cost_per_1m_tokens: float | None
    created_at: datetime
    updated_at: datetime
