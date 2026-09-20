from batch4llm.celery.worker import app
from celery.utils.log import get_task_logger
from batch4llm.config import ServiceSettings
from batch4llm.manager.database import Database
from batch4llm.manager.database.models.batch import Batch, BatchStatus, LogLevel
from batch4llm.manager.database.models.llm_request import LlmRequestStatus
from batch4llm.manager.file_storage import MinIOStorage
from batch4llm.manager.file_manager import FileManager
from batch4llm.manager.llm_client.client_manager import ClientManager
from batch4llm.manager.llm_client.models.exceptions import RateLimitError
from batch4llm.manager.price_calculator import calculate_price

service_settings = ServiceSettings()
logger = get_task_logger(__name__)
db = Database(service_settings.postgres_dsn)


def retry_or_finalize_batch_task(batch_id: int, batch_task_id: int, prompt: str):
    """Requeue a failed attempt if the task still has retry budget left,
    otherwise finalize the batch task as failed. This is the single place
    that decides the fate of a task after an unknown/generic failure -
    rate-limit failures never go through here, they are always retried
    (see the RateLimitError handling below)."""
    batch = db.worker.get_batch_by_id(batch_id)
    attempts = db.worker.count_attempts_for_batch_task(batch_task_id)
    if attempts <= batch.retries_per_failed_task:
        db.batches.create_retry_request(batch_task_id, prompt)
    else:
        db.batches.mark_batch_task_failed(batch_task_id)


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

    except RateLimitError as e:
        logger.warning(
            f"Rate limit hit while processing file {file_id} for llm_request {llm_request_id}: {e}"
        )

        db.batches.update_llm_request_status(
            llm_request_id=llm_request_id,
            status=LlmRequestStatus.FAILED,
            error=str(e),
        )
        if batch_task_id:
            db.batches.add_task_log(
                batch_task_id=batch_task_id,
                message=f"Rate limited while processing file: {file_id}: {str(e)}",
                level=LogLevel.WARN,
            )

            batch = db.worker.get_batch_by_id(batch_id)
            batch_stopped = False
            if batch.adaptive_rate_limiting:
                previous_rate = batch.max_tasks_per_minute
                batch = db.batches.apply_rate_limit_backoff(batch_id)
                if batch.max_tasks_per_minute < previous_rate:
                    db.batches.add_batch_log(
                        batch_id=batch_id,
                        message=(
                            f"Rate limit hit: throttling from {previous_rate:.2f} "
                            f"to {batch.max_tasks_per_minute:.2f} tasks/min."
                        ),
                        level=LogLevel.WARN,
                    )
                if batch.max_tasks_per_minute < Batch.ADAPTIVE_RATE_FAIL_THRESHOLD:
                    db.batches.update_status(batch_id, BatchStatus.FAILED)
                    db.batches.add_batch_log(
                        batch_id=batch_id,
                        message=(
                            "Batch stopped: request rate dropped below "
                            f"{Batch.ADAPTIVE_RATE_FAIL_THRESHOLD}/min after "
                            "repeated rate-limit errors."
                        ),
                        level=LogLevel.ERROR,
                    )
                    batch_stopped = True

            if not batch_stopped:
                # Rate limits are never the task's fault: always retry,
                # regardless of the retry budget.
                db.batches.create_retry_request(batch_task_id, llm_request.prompt)
        return {
            "status": "failed",
            "llm_request_id": llm_request_id,
            "error": str(e),
        }

    except Exception as e:
        logger.exception(e)

        db.batches.update_llm_request_status(
            llm_request_id=llm_request_id,
            status=LlmRequestStatus.FAILED,
            error=str(e),
        )
        if batch_task_id:
            db.batches.add_task_log(
                batch_task_id=batch_task_id,
                message=f"Error while processing file: {file_id}: {str(e)}",
                level=LogLevel.ERROR,
            )
            retry_or_finalize_batch_task(batch_id, batch_task_id, llm_request.prompt)
        return {
            "status": "failed",
            "llm_request_id": llm_request_id,
            "error": str(e),
        }
