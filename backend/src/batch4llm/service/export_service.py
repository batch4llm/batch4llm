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
            for batch_tasks in batch_export.batch_tasks:
                long_format.append(
                    {
                        "batch_id": batch_id,
                        "batch_task_id": batch_tasks.id,
                        "status": str(batch_tasks.status),
                        "client": batch_export.endpoint.client,
                        "provider": batch_export.endpoint.provider,
                        "model": batch_export.batch.model,
                        "temperature": batch_export.batch.temperature,
                        "file_name": file_by_id[batch_tasks.file_id].name,
                        "prompt_marker": batch_tasks.prompt_marker,
                        "output": batch_tasks.output,
                    }
                )
            results.extend(long_format)
            pass
        exporter = BatchExporter(mode)
        return exporter.export(results)
