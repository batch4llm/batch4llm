from datetime import datetime
from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=30)
    content: str = Field(..., min_length=3)
    multi_prompt: bool = False


class PromptData(BaseModel):
    id: int
    name: str
    content: str
    multi_prompt: bool
    step_count: int | None = None
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None = None
