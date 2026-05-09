from datetime import datetime, timedelta
from sqlalchemy import func, and_, select
from sqlalchemy.orm import sessionmaker, aliased

from batch4llm.manager.database.models.batch_file import BatchFile
from batch4llm.manager.database.models.batch_task import BatchTask, BatchTaskStatus
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

    def count_running_tasks_on_batch(self, batch_id: int):
        with self.SessionLocal() as session:
            return (
                session.query(func.count(BatchTask.id))
                .filter(
                    BatchTask.batch_id == batch_id,
                    BatchTask.status == BatchTaskStatus.RUNNING,
                )
                .scalar()
            )

    def count_started_in_last_minute_tasks_on_batch(self, batch_id: int):
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        with self.SessionLocal() as session:
            return (
                session.query(func.count(BatchTask.id))
                .filter(
                    BatchTask.batch_id == batch_id,
                    and_(
                        BatchTask.started_at is not None,
                        BatchTask.started_at >= one_minute_ago,
                    ),
                )
                .scalar()
            )

    def get_queued_task_from_batch_id(self, batch_id: int) -> BatchTask | None:
        with self.SessionLocal() as session:
            return (
                session.query(BatchTask)
                .filter(
                    BatchTask.batch_id == batch_id,
                    BatchTask.status == BatchTaskStatus.QUEUED,
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

    def get_failed_tasks_with_open_retry(self) -> list[BatchTask]:
        with self.SessionLocal() as session:
            RetryTask = aliased(BatchTask)

            # count retries of root task
            retry_count = (
                select(func.count(RetryTask.id))
                .where(RetryTask.retry_of_batch_task_id == BatchTask.id)
                .correlate(BatchTask)
                .scalar_subquery()
            )

            # does a retry already exists
            open_retry_exists = (
                select(RetryTask.id)
                .where(
                    RetryTask.retry_of_batch_task_id == BatchTask.id,
                    RetryTask.status.in_(
                        [
                            BatchTaskStatus.QUEUED,
                            BatchTaskStatus.RUNNING,
                        ]
                    ),
                )
                .correlate(BatchTask)
                .exists()
            )

            stmt = (
                select(BatchTask)
                .join(BatchTask.batch)
                .where(
                    Batch.status == BatchStatus.RUNNING,
                    BatchTask.status == BatchTaskStatus.FAILED,
                    BatchTask.retry_of_batch_task_id.is_(None),
                    retry_count < Batch.retries_per_failed_task,
                    ~open_retry_exists,
                )
            )

            return list(session.execute(stmt).scalars().all())

    def get_running_batch_tasks(self) -> list[BatchTask]:
        with self.SessionLocal() as session:
            return list(
                session.scalars(
                    select(BatchTask).where(BatchTask.status == BatchTaskStatus.RUNNING)
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

    def get_queued_tasks_for_batch(self, batch_id: int) -> list[BatchTask]:
        with self.SessionLocal() as session:
            return (
                session.query(BatchTask)
                .filter_by(batch_id=batch_id, status=BatchTaskStatus.QUEUED)
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
