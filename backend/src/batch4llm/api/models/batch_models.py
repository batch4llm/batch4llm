from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional

from batch4llm.manager.database.models.batch_task import BatchTaskStatus
from batch4llm.manager.database.models.llm_request import LlmRequestStatus

OUTPUT_PREVIEW_LENGTH = 500


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
    archived_at: Optional[datetime] = None


class BatchFileOverviewData(BaseModel):
    id: int
    batch_id: int
    file_id: int
    name: str
    status: str
    task_count: int
    completed_task_count: int
    created_at: datetime
    updated_at: datetime


class BatchTaskPreviewData(BaseModel):
    id: int
    batch_file_id: int
    status: str
    prompt_marker: Optional[str] = None
    depends_on_batch_task_id: Optional[int] = None
    output_preview: Optional[str] = None
    output_truncated: bool
    retry_count: int
    input_token_count: Optional[int] = None
    output_token_count: Optional[int] = None
    costs_in_usd: Optional[float] = None
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class BatchFileDetailData(BaseModel):
    id: int
    batch_id: int
    file_id: int
    name: str
    status: str
    batch_tasks: list[BatchTaskPreviewData]
    input_token_count: int
    output_token_count: int
    costs_in_usd: float
    created_at: datetime
    updated_at: datetime


class LlmAttemptData(BaseModel):
    """One LLM attempt (a retry) of a task. Failed attempts carry no output.

    The frontend derives the task's result from these: the winning attempt is
    the first COMPLETED one, total cost is the sum, and the retry count is the
    number of attempts minus one. `reason` is a placeholder until LlmRequest
    carries a dedicated error field.
    """

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: int
    status: LlmRequestStatus
    output: Optional[str] = None
    reason: Optional[str] = Field(default=None, validation_alias="error")
    input_token_count: Optional[int] = None
    output_token_count: Optional[int] = None
    costs_in_usd: Optional[float] = None
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class BatchTaskDetailData(BaseModel):
    """Full task detail: the task's own columns, its effective prompt/input,
    and the raw list of attempts. All result aggregation happens client-side.
    """

    model_config = ConfigDict(
        from_attributes=True, use_enum_values=True, populate_by_name=True
    )

    id: int
    batch_id: int
    batch_file_id: int
    file_id: int
    status: BatchTaskStatus
    prompt_marker: Optional[str] = None
    depends_on_batch_task_id: Optional[int] = None
    system_prompt: Optional[str] = None
    user_input: Optional[str] = None
    attempts: List[LlmAttemptData] = Field(
        default_factory=list, validation_alias="llm_requests"
    )
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
