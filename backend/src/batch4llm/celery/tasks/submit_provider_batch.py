from io import BytesIO

from batch4llm.celery.worker import app
from celery.utils.log import get_task_logger
from batch4llm.config import ServiceSettings
from batch4llm.manager.database import Database
from batch4llm.manager.database.models.batch import BatchStatus, LogLevel
from batch4llm.manager.file_manager import FileManager
from batch4llm.manager.file_reader.reader_manager import FileReaderManager
from batch4llm.manager.file_storage import MinIOStorage
from batch4llm.manager.llm_client.client_manager import ClientManager
from batch4llm.manager.llm_client.models.model_settings_model import ModelSettings

service_settings = ServiceSettings()
logger = get_task_logger(__name__)
db = Database(service_settings.postgres_dsn)


@app.task
def submit_provider_batch(batch_id: int):
    file_storage = MinIOStorage(
        service_settings.minio_endpoint,
        service_settings.minio_access_key,
        service_settings.minio_secret_key,
        service_settings.minio_bucket,
    )
    file_manager = FileManager(file_storage, db)
    client_manager = ClientManager()

    try:
        batch = db.worker.get_batch_by_id(batch_id)
        endpoint = db.worker.get_endpoint(batch.endpoint_id)
        client = client_manager.get_client(endpoint)

        if not client.supports_provider_batch():
            raise ValueError(
                f"Provider '{endpoint['client']}' does not support the batch API."
            )

        tasks = db.worker.get_queued_tasks_for_batch(batch_id)
        if not tasks:
            raise ValueError(f"No queued tasks found for batch {batch_id}.")

        model_settings = ModelSettings(
            temperature=batch.temperature,
            json_format=batch.json_format,
            top_p=batch.top_p,
            top_k=batch.top_k,
            max_output_tokens=batch.max_output_tokens,
        )

        for task in tasks:
            file = file_manager.download_intern(task.file_id)
            if batch.file_reader == "upload":
                include_file = file
                content = None
            else:
                include_file = None
                content = FileReaderManager.read(batch.file_reader, file.data)

            client.add_to_batch(
                custom_id=str(task.id),
                model=batch.model,
                prompt=task.prompt,
                file=include_file,
                content=content,
                model_settings=model_settings,
            )

        provider_batch_id, jsonl_bytes = client.submit_batch()

        jsonl_path = f"provider-batches/{batch_id}.jsonl"
        file_storage.upload(jsonl_path, BytesIO(jsonl_bytes), len(jsonl_bytes))

        db.batches.update_provider_batch_submitted(batch_id, provider_batch_id)
        db.batches.add_batch_log(
            batch_id=batch_id,
            message=f"Provider batch submitted successfully. Provider ID: {provider_batch_id}",
        )
        logger.info(f"Batch {batch_id} submitted to provider: {provider_batch_id}")

    except Exception as e:
        logger.exception(e)
        db.batches.update_status(batch_id, BatchStatus.FAILED)
        db.batches.add_batch_log(
            batch_id=batch_id,
            message=f"Provider batch submission failed: {str(e)}",
            level=LogLevel.ERROR,
        )
