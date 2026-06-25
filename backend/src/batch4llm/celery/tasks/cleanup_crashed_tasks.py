from batch4llm.celery.worker import app
from celery.utils.log import get_task_logger
from batch4llm.config import ServiceSettings
from batch4llm.manager.database import Database
from celery.result import AsyncResult
from batch4llm.manager.database.models.llm_request import LlmRequestStatus

service_settings = ServiceSettings()
logger = get_task_logger(__name__)
db = Database(service_settings.postgres_dsn)


@app.task
def cleanup_crashed_tasks():
    for request in db.worker.get_running_llm_requests():
        if not request.worker_task_id:
            db.batches.update_llm_request_status(request.id, LlmRequestStatus.FAILED)
            continue

        result = AsyncResult(request.worker_task_id, app=app)

        if result.state == "SUCCESS":
            logger.warning(
                f"LlmRequest {request.id} succeeded in Celery but never updated DB"
            )
            db.batches.update_llm_request_status(request.id, LlmRequestStatus.FAILED)
        elif result.state in ["FAILURE", "REVOKED"]:
            logger.warning(f"LlmRequest {request.id} is dead with state {result.state}")
            db.batches.update_llm_request_status(request.id, LlmRequestStatus.FAILED)
