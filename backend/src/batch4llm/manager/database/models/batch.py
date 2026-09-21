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

    endpoint_id: Mapped[int | None] = mapped_column(
        ForeignKey("endpoints.id", ondelete="SET NULL"), nullable=True
    )
    endpoint_name: Mapped[str | None] = mapped_column(nullable=True)
    prompt_id: Mapped[int | None] = mapped_column(
        ForeignKey("prompts.id", ondelete="SET NULL"), nullable=True
    )
    prompt_name: Mapped[str | None] = mapped_column(nullable=True)
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

    max_tasks_per_minute: Mapped[float] = mapped_column(Float, nullable=False)
    allow_concurrency: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    adaptive_rate_limiting: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    last_rate_limit_hit_at: Mapped[datetime | None] = mapped_column(nullable=True)
    last_rate_recovery_at: Mapped[datetime | None] = mapped_column(nullable=True)
    retries_per_failed_task: Mapped[int] = mapped_column(Integer, nullable=False)
    failure_threshold_percent: Mapped[float] = mapped_column(Float, nullable=False)
    queue_batch: Mapped[bool] = mapped_column(Boolean, nullable=False)

    scheduled_at: Mapped[datetime | None] = mapped_column(nullable=True)
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

    # ── Adaptive rate limiting tuning (AIMD) ─────────────────────────────
    # Additive-increase/multiplicative-decrease throttling of
    # `max_tasks_per_minute` for batches with `adaptive_rate_limiting=True`.
    # See dispatch_database_tasks.py (pacing/recovery) and
    # process_single_file.py (backoff on RateLimitError).
    ADAPTIVE_RATE_START = 5.0
    ADAPTIVE_RATE_DECREASE_FACTOR = 0.5
    ADAPTIVE_RATE_RECOVERY_STEP = 1.0
    ADAPTIVE_RATE_RECOVERY_INTERVAL_SECONDS = 60
    ADAPTIVE_RATE_COOLDOWN_INTERVALS = 3
    ADAPTIVE_RATE_SANITY_MAX = 150.0
    # Below this, a batch is considered permanently rate-limited and is failed.
    ADAPTIVE_RATE_FAIL_THRESHOLD = 0.025
    ADAPTIVE_MAX_DISPATCH_SLOTS_PER_TICK = 10


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
