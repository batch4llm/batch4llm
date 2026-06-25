import enum
from datetime import datetime

from sqlalchemy import ForeignKey, Enum, Integer, Text, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from batch4llm.manager.database.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .batch_task import BatchTask


class LlmRequestStatus(enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class LlmRequest(Base):
    __tablename__ = "llm_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_task_id: Mapped[int] = mapped_column(
        ForeignKey("batch_tasks.id"), nullable=False
    )

    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    input: Mapped[str] = mapped_column(Text, nullable=True)
    output: Mapped[str] = mapped_column(Text, nullable=True)
    input_token_count: Mapped[int] = mapped_column(Integer, nullable=True)
    output_token_count: Mapped[int] = mapped_column(Integer, nullable=True)
    seed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    costs_in_usd: Mapped[float] = mapped_column(Float, nullable=True)
    worker_task_id: Mapped[str] = mapped_column(Text, nullable=True)

    status: Mapped["LlmRequestStatus"] = mapped_column(
        Enum(LlmRequestStatus, name="llm_request_status_enum"),
        nullable=False,
        default=LlmRequestStatus.QUEUED,
    )

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=func.now(), onupdate=func.now()
    )
    started_at: Mapped[datetime] = mapped_column(nullable=True)
    stopped_at: Mapped[datetime] = mapped_column(nullable=True)

    batch_task: Mapped["BatchTask"] = relationship(back_populates="llm_requests")

    RUNNING_STATUSES = [LlmRequestStatus.RUNNING]
    STOPPED_STATUSES = [LlmRequestStatus.COMPLETED, LlmRequestStatus.FAILED]

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in self.__mapper__.columns}
