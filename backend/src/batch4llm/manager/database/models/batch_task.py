import enum
from datetime import datetime

from sqlalchemy import ForeignKey, Enum, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from batch4llm.manager.database.base import Base
from .batch_file import BatchFile
from .file import File
from .batch import BatchLogEntry, Batch
from .endpoint import Endpoint
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .llm_request import LlmRequest


class BatchTaskStatus(enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class BatchTask(Base):
    __tablename__ = "batch_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("batches.id"), nullable=False)
    batch_file_id: Mapped[int] = mapped_column(
        ForeignKey("batch_files.id"), nullable=False
    )
    file_id: Mapped[int] = mapped_column(ForeignKey("files.id"), nullable=False)
    endpoint_id: Mapped[int] = mapped_column(ForeignKey("endpoints.id"), nullable=False)

    status: Mapped["BatchTaskStatus"] = mapped_column(
        Enum(BatchTaskStatus, name="batch_task_status_enum"),
        nullable=False,
        default=BatchTaskStatus.QUEUED,
    )

    prompt_marker: Mapped[str] = mapped_column(Text, nullable=False)

    depends_on_batch_task_id: Mapped[int | None] = mapped_column(
        ForeignKey("batch_tasks.id"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=func.now(), onupdate=func.now()
    )
    started_at: Mapped[datetime] = mapped_column(nullable=True)
    stopped_at: Mapped[datetime] = mapped_column(nullable=True)

    batch: Mapped["Batch"] = relationship(back_populates="batch_tasks")
    batch_file: Mapped["BatchFile"] = relationship(back_populates="batch_tasks")
    file: Mapped["File"] = relationship()
    endpoint: Mapped["Endpoint"] = relationship()

    llm_requests: Mapped[list["LlmRequest"]] = relationship(
        back_populates="batch_task", cascade="all, delete-orphan"
    )

    batch_log_entries: Mapped[list["BatchLogEntry"]] = relationship(
        back_populates="batch_task"
    )

    RUNNING_STATUSES = [
        BatchTaskStatus.RUNNING,
    ]

    STOPPED_STATUSES = [
        BatchTaskStatus.COMPLETED,
        BatchTaskStatus.FAILED,
    ]

    def to_dict(self, include_llm_requests: bool = False) -> dict:
        data = {c.key: getattr(self, c.key) for c in self.__mapper__.columns}

        # Compute output/tokens/costs from successful LlmRequest if relationship is loaded
        loaded = self.__dict__.get("llm_requests")
        if loaded is not None:
            successful = next(
                (r for r in loaded if r.status.value == "COMPLETED"), None
            )
            data["output"] = successful.output if successful else None
            data["input_token_count"] = (
                successful.input_token_count if successful else None
            )
            data["output_token_count"] = (
                successful.output_token_count if successful else None
            )
            data["costs_in_usd"] = successful.costs_in_usd if successful else None
            if include_llm_requests:
                data["llm_requests"] = [r.to_dict() for r in loaded]
        else:
            data["output"] = None
            data["input_token_count"] = None
            data["output_token_count"] = None
            data["costs_in_usd"] = None

        return data
