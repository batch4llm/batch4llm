from datetime import datetime, timedelta, timezone

from batch4llm.celery.worker import app
from batch4llm.celery.tasks import process_single_file
from batch4llm.celery.tasks.submit_provider_batch import submit_provider_batch
from celery.utils.log import get_task_logger
from batch4llm.config import ServiceSettings
from batch4llm.manager.database import Database
from batch4llm.manager.database.models.batch import Batch, BatchStatus, LogLevel
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
        if batch.scheduled_at is None or batch.scheduled_at > datetime.now(
            timezone.utc
        ):
            continue

        if batch.use_provider_batch:
            db.batches.update_status(batch.id, BatchStatus.PROVIDER_BATCH_PENDING)
            db.batches.add_batch_log(
                batch_id=batch.id,
                message="Scheduled start time reached. Provider batch submission queued.",
            )
            submit_provider_batch.delay(batch.id)
        else:
            db.batches.update_status(batch.id, BatchStatus.QUEUED)
            db.batches.add_batch_log(
                batch_id=batch.id,
                message="Scheduled start time reached, batch is now queued.",
            )

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
                continue

        now = datetime.now(timezone.utc)

        if batch.adaptive_rate_limiting:
            in_cooldown = False
            if batch.last_rate_limit_hit_at is not None:
                cooldown_seconds = Batch.ADAPTIVE_RATE_COOLDOWN_INTERVALS * (
                    60.0 / batch.max_tasks_per_minute
                )
                in_cooldown = now < batch.last_rate_limit_hit_at + timedelta(
                    seconds=cooldown_seconds
                )

            if in_cooldown:
                # Still backing off from a recent rate-limit hit: dispatch
                # nothing for this batch this tick.
                continue

            batch = db.batches.advance_rate_recovery(batch.id)

        if (
            not batch.allow_concurrency
            and db.worker.count_running_requests_on_batch(batch.id) >= 1
        ):
            continue

        # Pacing: how many slots have accumulated since the last dispatched
        # request, given the batch's current (possibly AIMD-adjusted) rate.
        # This replaces a fixed per-tick dispatch with a token-bucket style
        # catch-up, so the effective rate isn't capped by this task's own
        # 5s schedule - and works just as well for sub-1/min rates.
        interval_seconds = 60.0 / batch.max_tasks_per_minute
        last_started_at = db.worker.get_last_request_started_at_for_batch(batch.id)
        if last_started_at is None:
            available_slots = 1
        else:
            elapsed_seconds = (now - last_started_at).total_seconds()
            if (
                batch.adaptive_rate_limiting
                and batch.last_rate_limit_hit_at is not None
            ):
                # Don't credit backlog that accumulated while dispatch was
                # paused during a rate-limit cooldown - otherwise the pause
                # itself builds up slack that fires as a burst the moment
                # the cooldown ends, immediately re-triggering the limit.
                cooldown_seconds = Batch.ADAPTIVE_RATE_COOLDOWN_INTERVALS * (
                    60.0 / batch.max_tasks_per_minute
                )
                cooldown_ended_at = batch.last_rate_limit_hit_at + timedelta(
                    seconds=cooldown_seconds
                )
                elapsed_seconds = min(
                    elapsed_seconds, (now - cooldown_ended_at).total_seconds()
                )
            available_slots = int(elapsed_seconds // interval_seconds)

        if not batch.allow_concurrency:
            available_slots = min(available_slots, 1)
        available_slots = min(
            available_slots, Batch.ADAPTIVE_MAX_DISPATCH_SLOTS_PER_TICK
        )

        for _ in range(max(0, available_slots)):
            request = db.worker.get_queued_llm_request_from_batch(batch.id)
            if not request:
                break

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
