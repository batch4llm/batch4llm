import enum
from datetime import datetime

from sqlalchemy import ForeignKey, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from batch4llm.manager.database.base import Base
from .file import File
from .batch import Batch, BatchLogEntry
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .batch_task import BatchTask


class BatchFileStatus(enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class BatchFile(Base):
    __tablename__ = "batch_files"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    batch_id: Mapped[int] = mapped_column(ForeignKey("batches.id"), nullable=False)
    file_id: Mapped[int] = mapped_column(ForeignKey("files.id"), nullable=False)
    status: Mapped["BatchFileStatus"] = mapped_column(
        Enum(BatchFileStatus, name="batch_file_status_enum"),
        nullable=False,
        default=BatchFileStatus.QUEUED,
    )

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=func.now(), onupdate=func.now()
    )

    batch: Mapped["Batch"] = relationship(back_populates="batch_files")
    file: Mapped["File"] = relationship()

    batch_tasks: Mapped[list["BatchTask"]] = relationship(
        back_populates="batch_file", cascade="all, delete-orphan"
    )

    batch_log_entries: Mapped[list["BatchLogEntry"]] = relationship(
        back_populates="batch_file"
    )

    ACTIVE_STATUSES = [
        BatchFileStatus.QUEUED,
        BatchFileStatus.RUNNING,
    ]
    STOPPED_STATUSES = [
        BatchFileStatus.COMPLETED,
        BatchFileStatus.FAILED,
    ]

    def to_dict(self, include_batch_tasks: bool = False) -> dict:
        data = {c.key: getattr(self, c.key) for c in self.__mapper__.columns}
        if include_batch_tasks:
            tasks_data = [
                task.to_dict(include_llm_requests=True) for task in self.batch_tasks
            ]
            data["batch_tasks"] = tasks_data
            # Aggregate costs/tokens from successful requests across all tasks
            data["costs_in_usd"] = (
                sum(t.get("costs_in_usd") or 0 for t in tasks_data) or None
            )
            data["input_token_count"] = sum(
                t.get("input_token_count") or 0 for t in tasks_data
            )
            data["output_token_count"] = sum(
                t.get("output_token_count") or 0 for t in tasks_data
            )
        return data
