from batch4llm.celery.worker import app
from celery.utils.log import get_task_logger
from batch4llm.config import ServiceSettings
from batch4llm.manager.database import Database
from batch4llm.manager.database.models.batch import LogLevel
from batch4llm.manager.database.models.batch_task import BatchTaskStatus
from batch4llm.manager.file_storage import MinIOStorage
from batch4llm.manager.file_manager import FileManager
from batch4llm.manager.llm_client.client_manager import ClientManager
from batch4llm.manager.price_calculator import calculate_price

service_settings = ServiceSettings()
logger = get_task_logger(__name__)
db = Database(service_settings.postgres_dsn)


@app.task(bind=True)
def process_single_file(
    self,
    batch_id,
    batch_task,
    endpoint,
    file_reader,
    model,
    prompt,
    temperature,
    json_format,
):
    file_storage = MinIOStorage(
        service_settings.minio_endpoint,
        service_settings.minio_access_key,
        service_settings.minio_secret_key,
        service_settings.minio_bucket,
    )
    file_manager = FileManager(file_storage, db)
    client_manager = ClientManager()

    try:
        db.batches.add_task_log(
            batch_task["id"],
            f"Processing file: {batch_task['file_id']} with endpoint {model} at {endpoint['name']}",
        )
        file = file_manager.download_intern(batch_task["file_id"])
        result = client_manager.process(
            endpoint=endpoint,
            file_reader=file_reader,
            file=file,
            model=model,
            prompt=prompt,
            temperature=temperature,
            json_format=json_format,
        )

        price = None
        if endpoint["provider"].lower() != "self_hosted":
            try:
                model_name = result.model.replace("models/", "")
                price = calculate_price(
                    result.input_tokens,
                    result.output_tokens,
                    endpoint["provider"],
                    model_name,
                )
            except Exception as e:
                logger.error(e)

        db.batches.update_batch_task_status(
            batch_task["id"],
            status=BatchTaskStatus.COMPLETED,
            engine_response=result,
            costs_in_usd=price,
        )
        db.batches.add_task_log(
            batch_task_id=batch_task["id"],
            message=f"Successfully processed batch task: {batch_task['id']}",
        )
        return {"status": "success", "batch_task_id": batch_task["id"]}

    except Exception as e:
        logger.exception(e)

        db.batches.update_batch_task_status(
            batch_task_id=batch_task["id"],
            status=BatchTaskStatus.FAILED,
        )
        db.batches.add_task_log(
            batch_task_id=batch_task["id"],
            message=f"Error while processing file: {batch_task['file_id']}: {str(e)}",
            level=LogLevel.ERROR,
        )
        return {"status": "failed", "batch_task_id": batch_task["id"], "error": str(e)}
