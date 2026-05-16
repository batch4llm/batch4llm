from typing import List

from sqlalchemy import func, asc
from sqlalchemy.orm import sessionmaker, selectinload
from batch4llm.manager.database.models.batch_task import BatchTask, BatchTaskStatus
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
                max_retries=batch_worker_settings.max_retries,
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
        retry_task_id: int = None,
    ):
        with self.SessionLocal() as session:
            batch = session.get(Batch, batch_id)
            if not batch:
                raise ValueError(f"Batch id '{batch_id}' not found.")
            if not session.get(File, file_id):
                raise ValueError(f"File id '{file_id}' not found.")
            if not session.get(BatchFile, batch_file_id):
                raise ValueError(f"BatchFile id '{batch_file_id}' not found.")

            root_task_id = None
            if retry_task_id:
                retry_task = session.get(BatchTask, retry_task_id)
                root_task_id = retry_task.root_task_id or retry_task_id

            new_batch_task = BatchTask(
                batch_id=batch_id,
                batch_file_id=batch_file_id,
                file_id=file_id,
                status=BatchTaskStatus.QUEUED,
                prompt=prompt,
                prompt_marker=prompt_marker,
                endpoint_id=batch.endpoint_id,
                retry_of_batch_task_id=retry_task_id,
                root_task_id=root_task_id,
            )

            session.add(new_batch_task)
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

    def update_batch_task_status(
        self,
        batch_task_id: int,
        status: BatchTaskStatus,
        worker_task_id: int = None,
        engine_response: LLMClientResponse = None,
        costs_in_usd: float = None,
    ):
        with self.SessionLocal() as session:
            batch_task = session.query(BatchTask).filter_by(id=batch_task_id).first()
            if not batch_task:
                raise ValueError(f"Batch Task id '{batch_task_id}' not found.")

            batch_task.status = status

            if status in BatchTask.RUNNING_STATUSES and not batch_task.started_at:
                batch_task.started_at = func.now()

            if status in BatchTask.STOPPED_STATUSES and not batch_task.stopped_at:
                batch_task.stopped_at = func.now()

            if worker_task_id:
                batch_task.worker_task_id = worker_task_id

            def _sanitize(value: str | None) -> str | None:
                if isinstance(value, str):
                    return value.replace("\x00", "")
                return value

            if engine_response:
                batch_task.input = _sanitize(engine_response.input)
                batch_task.output = _sanitize(engine_response.output)
                batch_task.input_token_count = engine_response.input_tokens
                batch_task.output_token_count = engine_response.output_tokens
                batch_task.seed = engine_response.seed
                batch_task.batch_file.input_token_count += engine_response.input_tokens
                batch_task.batch_file.output_token_count += (
                    engine_response.output_tokens
                )

            if costs_in_usd and batch_task.costs_in_usd is None:
                batch_task.costs_in_usd = costs_in_usd
                batch_task.batch.costs_in_usd = (
                    batch_task.batch.costs_in_usd or 0
                ) + costs_in_usd
                batch_task.batch_file.costs_in_usd = (
                    batch_task.batch_file.costs_in_usd or 0
                ) + costs_in_usd

            session.commit()
            session.refresh(batch_task)
            return batch_task

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

    def get_files(self, batch_id: int, user_id: int) -> List[dict]:
        with self.SessionLocal() as session:
            query = (
                session.query(Batch)
                .options(
                    selectinload(Batch.batch_files).selectinload(BatchFile.batch_tasks)
                )
                .filter_by(id=batch_id)
            )

            batch = Batch.accessible_by(query, user_id).first()

            if not batch:
                raise ValueError(f"Batch id '{batch_id}' not found.")

            return [bl.to_dict(include_batch_tasks=True) for bl in batch.batch_files]

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
            tasks = (
                session.query(BatchTask)
                .filter_by(batch_id=batch_id, status=BatchTaskStatus.QUEUED)
                .all()
            )
            for task in tasks:
                task.status = BatchTaskStatus.FAILED
                task.stopped_at = func.now()
            session.commit()

    def get_active_batches(self):
        with self.SessionLocal() as session:
            query = session.query(Batch).filter_by(status=BatchStatus.FAILED)
            batches = query.filter(Batch.status.in_(Batch.ACTIVE_STATUSES))
            return [b.to_dict() for b in batches]
