from batch4llm.celery.worker import app
from celery.utils.log import get_task_logger
from batch4llm.config import ServiceSettings
from batch4llm.manager.database import Database
from batch4llm.manager.database.models.batch import LogLevel
from batch4llm.manager.database.models.llm_request import LlmRequestStatus
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
    llm_request_id,
    file_id,
    file_path,
    prompt,
    endpoint,
    file_reader,
    model,
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

    llm_request = db.worker.get_llm_request_by_id(llm_request_id)
    batch_task_id = llm_request.batch_task_id if llm_request else None

    try:
        if batch_task_id:
            db.batches.add_task_log(
                batch_task_id,
                f"Processing file: {file_id} with endpoint {model} at {endpoint['name']}",
            )
        file = file_manager.download_intern(file_id)
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

        db.batches.update_llm_request_status(
            llm_request_id,
            status=LlmRequestStatus.COMPLETED,
            engine_response=result,
            costs_in_usd=price,
        )
        if batch_task_id:
            db.batches.add_task_log(
                batch_task_id=batch_task_id,
                message=f"Successfully processed llm request: {llm_request_id}",
            )
        return {"status": "success", "llm_request_id": llm_request_id}

    except Exception as e:
        logger.exception(e)

        db.batches.update_llm_request_status(
            llm_request_id=llm_request_id,
            status=LlmRequestStatus.FAILED,
        )
        if batch_task_id:
            db.batches.add_task_log(
                batch_task_id=batch_task_id,
                message=f"Error while processing file: {file_id}: {str(e)}",
                level=LogLevel.ERROR,
            )
        return {
            "status": "failed",
            "llm_request_id": llm_request_id,
            "error": str(e),
        }
