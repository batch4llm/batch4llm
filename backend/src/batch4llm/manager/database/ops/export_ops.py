from dataclasses import dataclass
from typing import List

from sqlalchemy.orm import sessionmaker, selectinload
from batch4llm.manager.database.models.batch_task import BatchTask
from batch4llm.manager.database.models.batch import (
    Batch,
)
from batch4llm.manager.database.models.batch_file import BatchFile
from batch4llm.manager.database.models.endpoint import Endpoint
from batch4llm.manager.database.models.file import File
from batch4llm.manager.database.models.prompt import Prompt


@dataclass
class BatchExport:
    batch: Batch
    endpoint: Endpoint
    prompt: Prompt
    files: List[File]
    batch_files: List[BatchFile]
    batch_tasks: List[BatchTask]


class ExportOps:
    def __init__(self, session_local: sessionmaker):
        self.SessionLocal = session_local

    def get_batch_for_export(self, batch_id: int, user_id: int) -> BatchExport:
        with self.SessionLocal() as session:
            query = (
                session.query(Batch)
                .options(
                    selectinload(Batch.batch_files).selectinload(BatchFile.file),
                    selectinload(Batch.batch_tasks).selectinload(
                        BatchTask.llm_requests
                    ),
                )
                .filter_by(id=batch_id)
            )

            batch = Batch.accessible_by(query, user_id).first()

            if not batch:
                raise ValueError(f"Batch id '{batch_id}' not found.")

            return BatchExport(
                batch=batch,
                endpoint=batch.endpoint,
                prompt=batch.prompt,
                files=[bf.file for bf in batch.batch_files],
                batch_files=batch.batch_files,
                batch_tasks=batch.batch_tasks,
            )
