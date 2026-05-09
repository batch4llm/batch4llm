from datetime import datetime

from pydantic import BaseModel, Field
from typing import List, Optional


class BatchWorkerSettings(BaseModel):
    max_tasks_per_minute: int = Field(..., gt=0, le=20)
    max_parallel_tasks: int = Field(..., gt=0, le=20)
    retries_per_failed_task: int = Field(..., gt=-1, le=20)
    max_retries: int = Field(..., gt=-1, le=20)
    queue_batch: bool = True


# -----      requests      -----
class BatchRunRequest(BaseModel):
    prompt_id: int
    files: List[int]
    endpoint_id: int
    file_reader: str
    model: str
    temperature: float = Field(..., ge=0.0, le=3.0)
    json_format: Optional[bool] = False
    use_provider_batch: bool = False
    # todo: implement/check limits
    batch_worker_settings: BatchWorkerSettings


# -----      data      -----
class BatchData(BaseModel):
    id: int
    name: str
    status: str
    prompt_id: int
    prompt_name: Optional[str] = None
    endpoint_id: int
    endpoint_name: Optional[str] = None
    progress: Optional[str] = None
    file_reader: str
    model: str
    temperature: float
    costs_in_usd: float
    use_provider_batch: Optional[bool] = None
    provider_batch_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime]
    stopped_at: Optional[datetime]


class BatchTaskData(BaseModel):
    id: int
    batch_id: int
    file_id: int
    status: str
    prompt_marker: Optional[str]
    output: Optional[str]
    input_token_count: Optional[int]
    output_token_count: Optional[int]
    costs_in_usd: Optional[float]
    created_at: datetime
    updated_at: datetime


class BatchFileData(BaseModel):
    id: int
    batch_id: int
    file_id: int
    name: str
    status: str
    input_token_count: Optional[int]
    output_token_count: Optional[int]
    costs_in_usd: Optional[float]
    batch_tasks: list[BatchTaskData]
    created_at: datetime
    updated_at: datetime
