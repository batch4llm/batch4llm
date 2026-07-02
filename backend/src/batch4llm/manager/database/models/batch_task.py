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

    # ── Derived task-level values ────────────────────────────────────────
    # A task owns one or more LlmRequests (one per attempt/retry). These
    # properties expose the task's effective result/prompt without callers
    # having to re-implement the "which attempt wins" rules. They read the
    # already-loaded `llm_requests` collection and return safe defaults when
    # it has not been eager-loaded, so they never trigger a lazy DB fetch.

    @property
    def _loaded_requests(self) -> list["LlmRequest"]:
        return self.__dict__.get("llm_requests") or []

    @property
    def _sorted_requests(self) -> list["LlmRequest"]:
        return sorted(self._loaded_requests, key=lambda r: r.created_at)

    @property
    def _successful_request(self) -> "LlmRequest | None":
        return next(
            (r for r in self._sorted_requests if r.status.value == "COMPLETED"), None
        )

    @property
    def retry_count(self) -> int:
        return max(0, len(self._loaded_requests) - 1)

    @property
    def output(self) -> str | None:
        req = self._successful_request
        return req.output if req else None

    @property
    def input_token_count(self) -> int | None:
        req = self._successful_request
        return req.input_token_count if req else None

    @property
    def output_token_count(self) -> int | None:
        req = self._successful_request
        return req.output_token_count if req else None

    @property
    def costs_in_usd(self) -> float | None:
        total = sum(r.costs_in_usd or 0.0 for r in self._loaded_requests)
        return total or None

    @property
    def system_prompt(self) -> str | None:
        # The system prompt is copied onto every attempt; the first is enough.
        reqs = self._sorted_requests
        return reqs[0].prompt if reqs else None

    @property
    def user_input(self) -> str | None:
        # The rendered user input is captured once a request runs; prefer the
        # successful attempt, fall back to any attempt that captured it.
        req = self._successful_request or next(
            (r for r in self._sorted_requests if r.input), None
        )
        return req.input if req else None

    def to_dict(self, include_llm_requests: bool = False) -> dict:
        data = {c.key: getattr(self, c.key) for c in self.__mapper__.columns}
        data["output"] = self.output
        data["input_token_count"] = self.input_token_count
        data["output_token_count"] = self.output_token_count
        data["costs_in_usd"] = self.costs_in_usd
        if include_llm_requests and self.__dict__.get("llm_requests") is not None:
            data["llm_requests"] = [r.to_dict() for r in self._loaded_requests]
        return data
