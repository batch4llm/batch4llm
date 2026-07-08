from typing import List, Optional, Tuple

from sqlalchemy import func, asc
from sqlalchemy.orm import sessionmaker, selectinload
from batch4llm.manager.database.models.batch_task import BatchTask, BatchTaskStatus
from batch4llm.manager.database.models.llm_request import LlmRequest, LlmRequestStatus
from batch4llm.manager.database.models.endpoint import Endpoint
from batch4llm.manager.database.models.prompt import Prompt
from batch4llm.manager.llm_client.models.response_model import LLMClientResponse
from batch4llm.manager.database.ops.user_ops import get_group_id_subquery
from batch4llm.manager.database.models.batch import (
    Batch,
    BatchStatus,
    BatchLogEntry,
    LogLevel,
)
from batch4llm.manager.database.models.batch_file import BatchFile, BatchFileStatus
from batch4llm.manager.database.models.file import File

_PREVIEW_LENGTH = 500


def _make_preview(
    output: Optional[str], length: int = _PREVIEW_LENGTH
) -> Tuple[Optional[str], bool]:
    if output is None:
        return None, False
    if len(output) <= length:
        return output, False
    return output[:length], True


class BatchOps:
    def __init__(self, session_local: sessionmaker):
        self.SessionLocal = session_local

    def add(
        self,
        name: str,
        status: BatchStatus,
        endpoint_id: int,
        prompt_id: int,
        file_reader: str,
        model: str,
        temperature: float,
        json_format: bool,
        user_id: int,
        batch_worker_settings,
        use_provider_batch: bool = False,
    ):
        with self.SessionLocal() as session:
            subq = get_group_id_subquery(session, user_id)

            batch = Batch(
                name=name,
                status=status,
                endpoint_id=endpoint_id,
                prompt_id=prompt_id,
                file_reader=file_reader,
                model=model,
                temperature=temperature,
                json_format=json_format,
                user_id=user_id,
                group_id=subq,
                use_provider_batch=use_provider_batch,
                max_tasks_per_minute=batch_worker_settings.max_tasks_per_minute,
                max_parallel_tasks=batch_worker_settings.max_parallel_tasks,
                retries_per_failed_task=batch_worker_settings.retries_per_failed_task,
                failure_threshold_percent=batch_worker_settings.failure_threshold_percent,
                queue_batch=batch_worker_settings.queue_batch,
            )

            session.add(batch)
            session.commit()
            session.refresh(batch)
            return batch.to_dict()

    def add_batch_file(
        self,
        batch_id: int,
        file_id: int,
    ):
        with self.SessionLocal() as session:
            batch = session.query(Batch).filter_by(id=batch_id).first()
            if not batch:
                raise ValueError(f"Batch id '{batch_id}' not found.")

            file = session.query(File).filter_by(id=file_id).first()
            if not file:
                raise ValueError(f"File id '{file_id}' not found.")

            new_batch_file = BatchFile(
                file_id=file_id,
                name=file.name,
                status=BatchFileStatus.QUEUED,
            )

            batch.batch_files.append(new_batch_file)

            session.commit()
            return new_batch_file.to_dict()

    def add_batch_task(
        self,
        batch_id: int,
        file_id: int,
        batch_file_id: int,
        prompt: str,
        prompt_marker: str,
    ):
        with self.SessionLocal() as session:
            batch = session.get(Batch, batch_id)
            if not batch:
                raise ValueError(f"Batch id '{batch_id}' not found.")
            if not session.get(File, file_id):
                raise ValueError(f"File id '{file_id}' not found.")
            if not session.get(BatchFile, batch_file_id):
                raise ValueError(f"BatchFile id '{batch_file_id}' not found.")

            new_batch_task = BatchTask(
                batch_id=batch_id,
                batch_file_id=batch_file_id,
                file_id=file_id,
                status=BatchTaskStatus.QUEUED,
                prompt_marker=prompt_marker,
                endpoint_id=batch.endpoint_id,
            )

            session.add(new_batch_task)
            session.flush()

            initial_request = LlmRequest(
                batch_task_id=new_batch_task.id,
                prompt=prompt,
                status=LlmRequestStatus.QUEUED,
            )
            session.add(initial_request)
            session.commit()
            return new_batch_task.to_dict()

    def update_status(
        self,
        batch_id: int,
        status: BatchStatus,
    ):
        with self.SessionLocal() as session:
            batch = session.query(Batch).filter_by(id=batch_id).first()
            if not batch:
                raise ValueError(f"Batch id '{batch_id}' not found.")

            if status in Batch.RUNNING_STATUSES and not batch.started_at:
                batch.started_at = func.now()

            if status in Batch.STOPPED_STATUSES and not batch.stopped_at:
                batch.stopped_at = func.now()

            batch.status = status

            session.commit()
            session.refresh(batch)
            return batch.to_dict()

    def update_batch_file_status(
        self,
        batch_file_id: int,
        status: BatchFileStatus,
    ):
        with self.SessionLocal() as session:
            batch_file = session.query(BatchFile).filter_by(id=batch_file_id).first()
            if not batch_file:
                raise ValueError(f"BatchFile '{batch_file_id}' not found.")

            batch_file.status = status

            session.commit()
            session.refresh(batch_file)
            return batch_file

    def update_llm_request_status(
        self,
        llm_request_id: int,
        status: LlmRequestStatus,
        worker_task_id: str = None,
        engine_response: LLMClientResponse = None,
        costs_in_usd: float = None,
    ):
        with self.SessionLocal() as session:
            llm_request = session.get(LlmRequest, llm_request_id)
            if not llm_request:
                raise ValueError(f"LlmRequest id '{llm_request_id}' not found.")

            batch_task = session.get(BatchTask, llm_request.batch_task_id)
            batch = session.get(Batch, batch_task.batch_id)

            llm_request.status = status

            if status in LlmRequest.RUNNING_STATUSES and not llm_request.started_at:
                llm_request.started_at = func.now()
                if batch_task.status == BatchTaskStatus.QUEUED:
                    batch_task.status = BatchTaskStatus.RUNNING
                    batch_task.started_at = func.now()

            if status in LlmRequest.STOPPED_STATUSES and not llm_request.stopped_at:
                llm_request.stopped_at = func.now()

            if worker_task_id:
                llm_request.worker_task_id = worker_task_id

            def _sanitize(value: str | None) -> str | None:
                if isinstance(value, str):
                    return value.replace("\x00", "")
                return value

            if engine_response:
                llm_request.input = _sanitize(engine_response.input)
                llm_request.output = _sanitize(engine_response.output)
                llm_request.input_token_count = engine_response.input_tokens
                llm_request.output_token_count = engine_response.output_tokens
                llm_request.seed = engine_response.seed

            if costs_in_usd:
                llm_request.costs_in_usd = costs_in_usd
                batch.costs_in_usd = (batch.costs_in_usd or 0) + costs_in_usd

            if status == LlmRequestStatus.COMPLETED:
                batch_task.status = BatchTaskStatus.COMPLETED
                batch_task.stopped_at = func.now()

            elif status == LlmRequestStatus.FAILED:
                retry_count = (
                    session.query(func.count(LlmRequest.id))
                    .filter(LlmRequest.batch_task_id == batch_task.id)
                    .scalar()
                )
                if retry_count <= batch.retries_per_failed_task:
                    new_request = LlmRequest(
                        batch_task_id=batch_task.id,
                        prompt=llm_request.prompt,
                        status=LlmRequestStatus.QUEUED,
                    )
                    session.add(new_request)
                else:
                    batch_task.status = BatchTaskStatus.FAILED
                    batch_task.stopped_at = func.now()

            session.commit()
            session.refresh(llm_request)
            return llm_request

    def add_task_log(
        self, batch_task_id: int, message: str, level: LogLevel = LogLevel.INFO
    ):
        with self.SessionLocal() as session:
            batch_task = session.query(BatchTask).filter_by(id=batch_task_id).first()
            if not batch_task:
                raise ValueError(
                    f"BatchTask with batch_task_id '{batch_task_id}' not found."
                )

            batch_log = BatchLogEntry(
                batch_id=batch_task.batch_id,
                batch_file_id=batch_task.batch_file_id,
                batch_task_id=batch_task.id,
                message=message,
                level=level,
            )

            session.add(batch_log)
            session.commit()
            session.refresh(batch_log)
            return batch_log.to_dict()

    def add_batch_log(
        self,
        batch_id: int,
        message: str,
        level: LogLevel = LogLevel.INFO,
        batch_file_id: int | None = None,
    ):
        with self.SessionLocal() as session:
            batch = session.query(Batch).filter_by(id=batch_id).first()
            if not batch:
                raise ValueError(f"Batch id '{batch_id}' not found.")
            if batch_file_id:
                batch_file = (
                    session.query(BatchFile).filter_by(id=batch_file_id).first()
                )
                if not batch_file:
                    raise ValueError(f"BatchFile '{batch_file_id}' not found.")

            batch_log = BatchLogEntry(
                batch_id=batch_id,
                batch_file_id=batch_file_id,
                message=message,
                level=level,
            )

            session.add(batch_log)
            session.commit()
            session.refresh(batch_log)
            return batch_log.to_dict()

    def get(self, batch_id: int, user_id: int) -> dict:
        with self.SessionLocal() as session:
            query = session.query(Batch).filter_by(id=batch_id)
            batch = Batch.accessible_by(query, user_id).first()
            if not batch:
                raise ValueError(f"Batch id '{batch_id}' not found.")
            return batch.to_dict()

    def get_files_overview(self, batch_id: int, user_id: int) -> List[dict]:
        with self.SessionLocal() as session:
            batch_query = session.query(Batch).filter_by(id=batch_id)
            batch = Batch.accessible_by(batch_query, user_id).first()
            if not batch:
                raise ValueError(f"Batch id '{batch_id}' not found.")

            batch_files = (
                session.query(BatchFile)
                .options(selectinload(BatchFile.batch_tasks))
                .filter_by(batch_id=batch_id)
                .all()
            )

            result = []
            for bf in batch_files:
                tasks = bf.batch_tasks
                result.append(
                    {
                        "id": bf.id,
                        "batch_id": bf.batch_id,
                        "file_id": bf.file_id,
                        "name": bf.name,
                        "status": bf.status.value,
                        "task_count": len(tasks),
                        "completed_task_count": sum(
                            1 for t in tasks if t.status.value == "COMPLETED"
                        ),
                        "created_at": bf.created_at,
                        "updated_at": bf.updated_at,
                    }
                )
            return result

    def get_file_with_tasks(self, file_id: int, user_id: int) -> dict:
        with self.SessionLocal() as session:
            query = (
                session.query(BatchFile)
                .options(
                    selectinload(BatchFile.batch_tasks).selectinload(
                        BatchTask.llm_requests
                    )
                )
                .filter_by(id=file_id)
            )
            batch_file = query.first()
            if not batch_file:
                raise ValueError(f"BatchFile id '{file_id}' not found.")

            batch_query = session.query(Batch).filter_by(id=batch_file.batch_id)
            if not Batch.accessible_by(batch_query, user_id).first():
                raise ValueError(f"BatchFile id '{file_id}' not found.")

            tasks_data = []
            for task in batch_file.batch_tasks:
                preview, truncated = _make_preview(task.output)
                tasks_data.append(
                    {
                        "id": task.id,
                        "batch_file_id": task.batch_file_id,
                        "status": task.status.value,
                        "prompt_marker": task.prompt_marker,
                        "depends_on_batch_task_id": task.depends_on_batch_task_id,
                        "output_preview": preview,
                        "output_truncated": truncated,
                        "retry_count": task.retry_count,
                        "input_token_count": task.input_token_count,
                        "output_token_count": task.output_token_count,
                        "costs_in_usd": task.costs_in_usd,
                        "started_at": task.started_at,
                        "stopped_at": task.stopped_at,
                        "created_at": task.created_at,
                        "updated_at": task.updated_at,
                    }
                )

            tasks = batch_file.batch_tasks
            return {
                "id": batch_file.id,
                "batch_id": batch_file.batch_id,
                "file_id": batch_file.file_id,
                "name": batch_file.name,
                "status": batch_file.status.value,
                "batch_tasks": tasks_data,
                "costs_in_usd": sum(t.costs_in_usd or 0.0 for t in tasks),
                "input_token_count": sum(t.input_token_count or 0 for t in tasks),
                "output_token_count": sum(t.output_token_count or 0 for t in tasks),
                "created_at": batch_file.created_at,
                "updated_at": batch_file.updated_at,
            }

    def get_task_detail(self, task_id: int, user_id: int) -> BatchTask:
        # Returns the ORM task with its attempts eager-loaded; the API layer
        # shapes it via BatchTaskDetailData.model_validate and the frontend
        # derives the result/cost/retry values from the attempts.
        with self.SessionLocal() as session:
            task = (
                session.query(BatchTask)
                .options(selectinload(BatchTask.llm_requests))
                .filter_by(id=task_id)
                .first()
            )
            if not task:
                raise ValueError(f"BatchTask id '{task_id}' not found.")

            batch_query = session.query(Batch).filter_by(id=task.batch_id)
            if not Batch.accessible_by(batch_query, user_id).first():
                raise ValueError(f"BatchTask id '{task_id}' not found.")

            return task

    def get_batch_log(self, batch_id: int, user_id: int, after_id: int = None) -> list:
        with self.SessionLocal() as session:
            batch_query = session.query(Batch).filter_by(id=batch_id)
            batch = Batch.accessible_by(batch_query, user_id).first()
            if not batch:
                raise ValueError(f"Batch id '{batch_id}' not found.")

            query = session.query(BatchLogEntry).filter(
                BatchLogEntry.batch_id == batch_id
            )
            if after_id:
                query = query.filter(BatchLogEntry.id > after_id)

            return [
                bl.to_dict()
                for bl in query.order_by(asc(BatchLogEntry.created_at)).all()
            ]

    def list(self, user_id: int, archived: bool | None = None):
        with self.SessionLocal() as session:
            query = Batch.accessible_by(session.query(Batch), user_id)
            query = Batch.filter_archived(query, archived)
            batches = (
                query.outerjoin(Prompt, Batch.prompt_id == Prompt.id)
                .outerjoin(Endpoint, Batch.endpoint_id == Endpoint.id)
                .add_columns(
                    Prompt.name.label("prompt_name"),
                    Endpoint.name.label("endpoint_name"),
                )
                .all()
            )
            result = []
            for batch, prompt_name, endpoint_name in batches:
                batch_dict = batch.to_dict()

                total_files = len(batch.batch_files)

                processed_files = sum(
                    1 for bf in batch.batch_files if bf.status != BatchFileStatus.QUEUED
                )

                batch_dict["progress"] = f"{processed_files}/{total_files}"
                batch_dict["prompt_name"] = prompt_name
                batch_dict["endpoint_name"] = endpoint_name
                result.append(batch_dict)
            return result

    def set_archived(self, batch_id: int, user_id: int, archived: bool) -> dict:
        with self.SessionLocal() as session:
            query = session.query(Batch).filter_by(id=batch_id)
            batch = Batch.accessible_by(query, user_id).first()
            if not batch:
                raise ValueError(f"Batch id '{batch_id}' not found.")
            batch.archived_at = func.now() if archived else None
            session.commit()
            session.refresh(batch)
            return batch.to_dict()

    def update_provider_batch_submitted(self, batch_id: int, provider_batch_id: str):
        with self.SessionLocal() as session:
            batch = session.query(Batch).filter_by(id=batch_id).first()
            if not batch:
                raise ValueError(f"Batch id '{batch_id}' not found.")
            batch.provider_batch_id = provider_batch_id
            batch.started_at = func.now()
            session.commit()
            session.refresh(batch)
            return batch.to_dict()

    def fail_all_queued_tasks(self, batch_id: int):
        with self.SessionLocal() as session:
            active_task_ids = (
                session.query(BatchTask.id)
                .filter(
                    BatchTask.batch_id == batch_id,
                    BatchTask.status.in_(
                        [BatchTaskStatus.QUEUED, BatchTaskStatus.RUNNING]
                    ),
                )
                .subquery()
            )

            session.query(LlmRequest).filter(
                LlmRequest.batch_task_id.in_(active_task_ids),
                LlmRequest.status.in_(
                    [LlmRequestStatus.QUEUED, LlmRequestStatus.RUNNING]
                ),
            ).update(
                {
                    LlmRequest.status: LlmRequestStatus.FAILED,
                    LlmRequest.stopped_at: func.now(),
                },
                synchronize_session=False,
            )

            session.query(BatchTask).filter(
                BatchTask.batch_id == batch_id,
                BatchTask.status.in_([BatchTaskStatus.QUEUED, BatchTaskStatus.RUNNING]),
            ).update(
                {
                    BatchTask.status: BatchTaskStatus.FAILED,
                    BatchTask.stopped_at: func.now(),
                },
                synchronize_session=False,
            )

            session.commit()

    def get_active_batches(self):
        with self.SessionLocal() as session:
            query = session.query(Batch).filter_by(status=BatchStatus.FAILED)
            batches = query.filter(Batch.status.in_(Batch.ACTIVE_STATUSES))
            return [b.to_dict() for b in batches]
