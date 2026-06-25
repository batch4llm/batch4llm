from datetime import datetime, timedelta
from sqlalchemy import func, and_, select
from sqlalchemy.orm import sessionmaker, selectinload, aliased

from batch4llm.manager.database.models.batch_file import BatchFile
from batch4llm.manager.database.models.batch_task import BatchTask, BatchTaskStatus
from batch4llm.manager.database.models.llm_request import LlmRequest, LlmRequestStatus
from batch4llm.manager.database.models.batch import (
    Batch,
    BatchStatus,
)
from batch4llm.manager.database.models.endpoint import Endpoint
from batch4llm.manager.database.models.file import File


class WorkerOps:
    def __init__(self, session_local: sessionmaker):
        self.SessionLocal = session_local

    def get_batches_with_status(self, status: BatchStatus) -> list[Batch]:
        with self.SessionLocal() as session:
            batches = session.query(Batch).filter_by(status=status).all()
            return batches

    def check_for_running_batch_on_endpoint(self, endpoint_id: int) -> bool:
        with self.SessionLocal() as session:
            return (
                session.query(Batch.id)
                .filter(
                    Batch.endpoint_id == endpoint_id,
                    Batch.status == BatchStatus.RUNNING,
                )
                .limit(1)
                .first()
                is not None
            )

    def count_running_requests_on_batch(self, batch_id: int) -> int:
        with self.SessionLocal() as session:
            return (
                session.query(func.count(LlmRequest.id))
                .join(BatchTask, LlmRequest.batch_task_id == BatchTask.id)
                .filter(
                    BatchTask.batch_id == batch_id,
                    LlmRequest.status == LlmRequestStatus.RUNNING,
                )
                .scalar()
            )

    def count_started_in_last_minute_requests_on_batch(self, batch_id: int) -> int:
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        with self.SessionLocal() as session:
            return (
                session.query(func.count(LlmRequest.id))
                .join(BatchTask, LlmRequest.batch_task_id == BatchTask.id)
                .filter(
                    BatchTask.batch_id == batch_id,
                    and_(
                        LlmRequest.started_at.isnot(None),
                        LlmRequest.started_at >= one_minute_ago,
                    ),
                )
                .scalar()
            )

    def get_queued_llm_request_from_batch(self, batch_id: int) -> LlmRequest | None:
        with self.SessionLocal() as session:
            DependentTask = aliased(BatchTask)

            # Unsatisfied dependency: depends_on task exists but is not COMPLETED
            dep_unsatisfied = (
                select(DependentTask.id)
                .where(
                    DependentTask.id == BatchTask.depends_on_batch_task_id,
                    DependentTask.status != BatchTaskStatus.COMPLETED,
                )
                .correlate(BatchTask)
                .exists()
            )

            return (
                session.query(LlmRequest)
                .options(selectinload(LlmRequest.batch_task))
                .join(BatchTask, LlmRequest.batch_task_id == BatchTask.id)
                .filter(
                    BatchTask.batch_id == batch_id,
                    LlmRequest.status == LlmRequestStatus.QUEUED,
                    BatchTask.status.notin_(BatchTask.STOPPED_STATUSES),
                    ~dep_unsatisfied,
                )
                .first()
            )

    def get_running_batch_files_with_no_pending_task(self):
        with self.SessionLocal() as session:
            pending_tasks = session.query(BatchTask.batch_file_id).filter(
                BatchTask.status.in_([BatchTaskStatus.QUEUED, BatchTaskStatus.RUNNING])
            )
            return (
                session.query(BatchFile)
                .filter(
                    BatchFile.status.in_(BatchFile.ACTIVE_STATUSES),
                    ~BatchFile.id.in_(pending_tasks),
                )
                .all()
            )

    def get_running_batches_with_no_pending_task(self):
        with self.SessionLocal() as session:
            pending_tasks = session.query(BatchTask.batch_id).filter(
                BatchTask.status.in_([BatchTaskStatus.QUEUED, BatchTaskStatus.RUNNING])
            )
            return (
                session.query(Batch)
                .filter(
                    Batch.status == BatchStatus.RUNNING, ~Batch.id.in_(pending_tasks)
                )
                .all()
            )

    def count_failed_task_of_batch(self, batch_id) -> int:
        with self.SessionLocal() as session:
            return (
                session.query(BatchTask)
                .filter_by(batch_id=batch_id, status=BatchTaskStatus.FAILED)
                .count()
            )

    def get_running_llm_requests(self) -> list[LlmRequest]:
        with self.SessionLocal() as session:
            return list(
                session.scalars(
                    select(LlmRequest)
                    .options(selectinload(LlmRequest.batch_task))
                    .where(LlmRequest.status == LlmRequestStatus.RUNNING)
                )
            )

    def get_endpoint(self, endpoint_id: int):
        with self.SessionLocal() as session:
            endpoint = (
                session.query(Endpoint)
                .filter_by(id=endpoint_id)
                .first()
                .to_dict_internal()
            )
            return endpoint

    def get_file_path(self, file_id: int) -> str:
        with self.SessionLocal() as session:
            file_path = session.query(File).filter_by(id=file_id).first().path
            return file_path

    def get_batch_by_id(self, batch_id: int) -> Batch:
        with self.SessionLocal() as session:
            batch = session.query(Batch).filter_by(id=batch_id).first()
            if not batch:
                raise ValueError(f"Batch id '{batch_id}' not found.")
            return batch

    def get_queued_llm_requests_for_batch(self, batch_id: int) -> list[LlmRequest]:
        with self.SessionLocal() as session:
            return (
                session.query(LlmRequest)
                .options(selectinload(LlmRequest.batch_task))
                .join(BatchTask, LlmRequest.batch_task_id == BatchTask.id)
                .filter(
                    BatchTask.batch_id == batch_id,
                    LlmRequest.status == LlmRequestStatus.QUEUED,
                )
                .all()
            )

    def get_provider_batch_pending_batches(self) -> list[Batch]:
        with self.SessionLocal() as session:
            return (
                session.query(Batch)
                .filter(
                    Batch.status == BatchStatus.PROVIDER_BATCH_PENDING,
                    Batch.provider_batch_id.isnot(None),
                )
                .all()
            )

    def get_llm_request_by_id(self, llm_request_id: int) -> LlmRequest | None:
        with self.SessionLocal() as session:
            return session.get(LlmRequest, llm_request_id)
