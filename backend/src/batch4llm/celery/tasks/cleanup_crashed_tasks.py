from batch4llm.celery.worker import app
from celery.utils.log import get_task_logger
from batch4llm.config import ServiceSettings
from batch4llm.manager.database import Database
from celery.result import AsyncResult
from batch4llm.manager.database.models.llm_request import LlmRequestStatus
from batch4llm.celery.tasks.process_single_file import retry_or_finalize_batch_task

service_settings = ServiceSettings()
logger = get_task_logger(__name__)
db = Database(service_settings.postgres_dsn)


def _fail_and_retry(request, error: str):
    db.batches.update_llm_request_status(
        request.id, LlmRequestStatus.FAILED, error=error
    )
    # A crashed worker is an unknown/generic failure, so it goes through the
    # same retry-budget decision as any other error in process_single_file.
    retry_or_finalize_batch_task(
        request.batch_task.batch_id, request.batch_task_id, request.prompt
    )


@app.task
def cleanup_crashed_tasks():
    for request in db.worker.get_running_llm_requests():
        if not request.worker_task_id:
            _fail_and_retry(request, error="No worker task was ever assigned.")
            continue

        result = AsyncResult(request.worker_task_id, app=app)

        if result.state == "SUCCESS":
            logger.warning(
                f"LlmRequest {request.id} succeeded in Celery but never updated DB"
            )
            _fail_and_retry(
                request, error="Task succeeded but the DB was never updated."
            )
        elif result.state in ["FAILURE", "REVOKED"]:
            logger.warning(f"LlmRequest {request.id} is dead with state {result.state}")
            _fail_and_retry(
                request, error=f"Worker task ended with state {result.state}."
            )
