import enum
from datetime import datetime

from sqlalchemy import ForeignKey, Enum, Integer, Text, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from batch4llm.manager.database.base import Base
from .batch_file import BatchFile
from .file import File
from .batch import BatchLogEntry, Batch
from .endpoint import Endpoint


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
        Enum(BatchTaskStatus, name="batch_file_status_enum"),
        nullable=False,
        default=BatchTaskStatus.QUEUED,
    )

    worker_task_id: Mapped[str] = mapped_column(Text, nullable=True)
    retry_of_batch_task_id: Mapped[int] = mapped_column(Integer, nullable=True)
    root_task_id: Mapped[int] = mapped_column(Integer, nullable=True)

    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_marker: Mapped[str] = mapped_column(Text, nullable=False)

    input: Mapped[str] = mapped_column(Text, nullable=True)
    output: Mapped[str] = mapped_column(Text, nullable=True)
    input_token_count: Mapped[int] = mapped_column(Integer, nullable=True)
    output_token_count: Mapped[int] = mapped_column(Integer, nullable=True)
    seed: Mapped[int | None] = mapped_column(Integer, nullable=True)

    costs_in_usd: Mapped[float] = mapped_column(Float, nullable=True)

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

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__mapper__.columns}
