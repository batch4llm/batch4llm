import enum
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, func, Enum, Integer, Float, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from batch4llm.manager.database.base import Base
from .resource_mixin import ResourceMixin

if TYPE_CHECKING:
    from .batch_file import BatchFile
    from .batch_task import BatchTask
    from .endpoint import Endpoint
    from .prompt import Prompt


class BatchStatus(enum.Enum):
    SCHEDULED = "SCHEDULED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    PROVIDER_BATCH_PENDING = "PROVIDER_BATCH_PENDING"
    COMPLETED = "COMPLETED"
    STOPPED = "STOPPED"
    FAILED = "FAILED"


class Batch(Base, ResourceMixin):
    __tablename__ = "batches"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    status: Mapped["BatchStatus"] = mapped_column(
        Enum(BatchStatus, name="batch_status_enum"), nullable=False
    )

    endpoint_id: Mapped[int] = mapped_column(ForeignKey("endpoints.id"), nullable=False)
    prompt_id: Mapped[int] = mapped_column(ForeignKey("prompts.id"), nullable=False)
    file_reader: Mapped[str] = mapped_column(nullable=False)
    model: Mapped[str] = mapped_column(nullable=False)
    temperature: Mapped[float] = mapped_column(nullable=False)
    json_format: Mapped[bool] = mapped_column(nullable=False)

    top_p: Mapped[float | None] = mapped_column(Float, nullable=True)
    top_k: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    context_window: Mapped[int | None] = mapped_column(Integer, nullable=True)

    costs_in_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    use_provider_batch: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    provider_batch_id: Mapped[str | None] = mapped_column(Text, nullable=True)

    max_tasks_per_minute: Mapped[int] = mapped_column(Integer, nullable=False)
    max_parallel_tasks: Mapped[int] = mapped_column(Integer, nullable=False)
    retries_per_failed_task: Mapped[int] = mapped_column(Integer, nullable=False)
    failure_threshold_percent: Mapped[float] = mapped_column(Float, nullable=False)
    queue_batch: Mapped[bool] = mapped_column(Boolean, nullable=False)

    started_at: Mapped[datetime] = mapped_column(nullable=True)
    stopped_at: Mapped[datetime] = mapped_column(nullable=True)

    endpoint: Mapped["Endpoint"] = relationship()
    prompt: Mapped["Prompt"] = relationship()

    batch_files: Mapped[list["BatchFile"]] = relationship(
        back_populates="batch", cascade="all, delete-orphan"
    )

    batch_tasks: Mapped[list["BatchTask"]] = relationship(
        back_populates="batch", cascade="all, delete-orphan"
    )

    batch_log_entries: Mapped[list["BatchLogEntry"]] = relationship(
        back_populates="batch", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__mapper__.columns}

    ACTIVE_STATUSES = [
        BatchStatus.RUNNING,
        BatchStatus.SCHEDULED,
        BatchStatus.QUEUED,
        BatchStatus.PROVIDER_BATCH_PENDING,
    ]

    RUNNING_STATUSES = [
        BatchStatus.RUNNING,
    ]

    STOPPED_STATUSES = [
        BatchStatus.STOPPED,
        BatchStatus.COMPLETED,
        BatchStatus.FAILED,
    ]


class LogLevel(enum.Enum):
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"


class BatchLogEntry(Base):
    __tablename__ = "batch_log_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("batches.id"), nullable=False)
    batch_file_id: Mapped[int] = mapped_column(
        ForeignKey("batch_files.id"), nullable=True
    )
    batch_task_id: Mapped[int] = mapped_column(
        ForeignKey("batch_tasks.id"), nullable=True
    )

    level: Mapped["LogLevel"] = mapped_column(
        Enum(LogLevel, name="log_level_enum"), nullable=False
    )
    message: Mapped[str] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())

    batch: Mapped["Batch"] = relationship(back_populates="batch_log_entries")
    batch_file: Mapped["BatchFile"] = relationship(back_populates="batch_log_entries")
    batch_task: Mapped["BatchTask"] = relationship(back_populates="batch_log_entries")

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__mapper__.columns}
