from io import BytesIO, StringIO
from typing import Union, Tuple
from batch4llm.manager.database import Database
from batch4llm.manager.exporter.exporter import BatchExporter


class ExportService:
    def __init__(self, db: Database):
        self.db = db

    def export_batches(
        self, batch_ids: list[int], mode: str, user_id: int
    ) -> Tuple[Union[StringIO, BytesIO], str, str]:
        results = []
        for batch_id in batch_ids:
            batch_export = self.db.export.get_batch_for_export(batch_id, user_id)
            long_format = []

            file_by_id = {f.id: f for f in batch_export.files}
            for task in batch_export.batch_tasks:
                successful_request = next(
                    (r for r in task.llm_requests if r.status.value == "COMPLETED"),
                    None,
                )
                long_format.append(
                    {
                        "batch_id": batch_id,
                        "batch_task_id": task.id,
                        "status": str(task.status),
                        "client": batch_export.endpoint.client,
                        "provider": batch_export.endpoint.provider,
                        "model": batch_export.batch.model,
                        "temperature": batch_export.batch.temperature,
                        "file_name": file_by_id[task.file_id].name,
                        "prompt_marker": task.prompt_marker,
                        "output": (
                            successful_request.output if successful_request else None
                        ),
                    }
                )
            results.extend(long_format)
        exporter = BatchExporter(mode)
        return exporter.export(results)
