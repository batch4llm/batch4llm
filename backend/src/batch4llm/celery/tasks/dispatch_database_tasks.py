from batch4llm.celery.worker import app
from batch4llm.celery.tasks import process_single_file
from celery.utils.log import get_task_logger
from batch4llm.config import ServiceSettings
from batch4llm.manager.database import Database
from batch4llm.manager.database.models.batch import BatchStatus, LogLevel
from batch4llm.manager.database.models.batch_file import BatchFileStatus
from batch4llm.manager.database.models.llm_request import LlmRequestStatus

service_settings = ServiceSettings()
logger = get_task_logger(__name__)
db = Database(service_settings.postgres_dsn)


@app.task
def dispatch_database_tasks():

    for batch_file in db.worker.get_running_batch_files_with_no_pending_task():
        db.batches.update_batch_file_status(batch_file.id, BatchFileStatus.COMPLETED)

    for batch in db.worker.get_running_batches_with_no_pending_task():
        db.batches.update_status(batch.id, BatchStatus.COMPLETED)
        db.batches.add_batch_log(
            batch_id=batch.id,
            message="Batch finished.",
        )

    scheduled_batches = db.worker.get_batches_with_status(BatchStatus.SCHEDULED)
    logger.debug(f"Fetched {len(scheduled_batches)} scheduled batches")
    for batch in scheduled_batches:
        # todo: check if scheduled date is passed and then queue the batch
        pass

    queued_batches = db.worker.get_batches_with_status(BatchStatus.QUEUED)
    logger.debug(f"Fetched {len(queued_batches)} queued batches")
    for batch in queued_batches:
        if not batch.queue_batch or not db.worker.check_for_running_batch_on_endpoint(
            batch.endpoint_id
        ):
            db.batches.update_status(batch.id, BatchStatus.RUNNING)
            db.batches.add_batch_log(
                batch_id=batch.id, message="Batch has just started."
            )
        else:
            logger.info(
                f"Batch {batch.id} can not start yet, the worker is still occupied by another batch!"
            )

    running_batches = db.worker.get_batches_with_status(BatchStatus.RUNNING)
    logger.debug(f"Fetched {len(running_batches)} running batches")
    for batch in running_batches:

        total_task_count = db.worker.count_total_task_of_batch(batch.id)
        if total_task_count > 0:
            failed_task_percent = (
                db.worker.count_failed_task_of_batch(batch.id) / total_task_count * 100
            )
            if failed_task_percent > batch.failure_threshold_percent:
                db.batches.update_status(batch.id, BatchStatus.FAILED)
                db.batches.add_batch_log(
                    batch_id=batch.id,
                    message="Batch exceeded the failure threshold and is set to failed. Already running API Request will be finished.",
                    level=LogLevel.ERROR,
                )
                # todo: set remaining batch files failed
                # todo: set remaining batch tasks failed

        if (
            db.worker.count_running_requests_on_batch(batch.id)
            >= batch.max_parallel_tasks
        ):
            continue
        if (
            db.worker.count_started_in_last_minute_requests_on_batch(batch.id)
            >= batch.max_tasks_per_minute
        ):
            continue

        request = db.worker.get_queued_llm_request_from_batch(batch.id)
        if request:
            endpoint = db.worker.get_endpoint(batch.endpoint_id)
            file_path = db.worker.get_file_path(request.batch_task.file_id)
            worker_task = process_single_file.delay(
                batch_id=batch.id,
                llm_request_id=request.id,
                file_id=request.batch_task.file_id,
                file_path=file_path,
                prompt=request.prompt,
                endpoint=endpoint,
                file_reader=batch.file_reader,
                model=batch.model,
                temperature=batch.temperature,
                json_format=batch.json_format,
            )
            db.batches.update_llm_request_status(
                request.id, LlmRequestStatus.RUNNING, worker_task_id=worker_task.id
            )
            db.batches.update_batch_file_status(
                request.batch_task.batch_file_id, BatchFileStatus.RUNNING
            )
