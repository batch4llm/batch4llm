from celery import Celery
from celery.signals import worker_process_init
from batch4llm.config import ServiceSettings
from batch4llm.manager.database.base import dispose_all_engines

service_settings = ServiceSettings()

app = Celery(
    "batch4llm_worker",
    broker=str(service_settings.redis_dsn),
    backend=str(service_settings.redis_dsn),
)

app.conf.beat_schedule = {
    "dispatch-database-tasks": {
        "task": "batch4llm.celery.tasks.dispatch_database_tasks.dispatch_database_tasks",
        "schedule": 5.0,
    },
    "cleanup-crashed-tasks": {
        "task": "batch4llm.celery.tasks.cleanup_crashed_tasks.cleanup_crashed_tasks",
        "schedule": 30.0,
    },
    "poll-provider-batches": {
        "task": "batch4llm.celery.tasks.poll_provider_batches.poll_provider_batches",
        "schedule": 60.0,
    },
    "sync-endpoint-models": {
        "task": "batch4llm.celery.tasks.sync_endpoint_models.sync_endpoint_models",
        "schedule": service_settings.model_sync_interval_minutes * 60.0,
    },
}
app.conf.task_track_started = True

app.autodiscover_tasks(["batch4llm.celery.tasks"])


@worker_process_init.connect
def _dispose_inherited_db_engines(**kwargs):
    """Drop pooled DB connections inherited from the parent process on fork.

    Task modules create their Database/engine at import time, which happens
    in the parent process before autodiscover_tasks's imports are forked out
    to worker children. Without this, forked children share the parent's
    pooled connections/sockets and corrupt libpq's protocol state under
    concurrent use.
    """
    dispose_all_engines()
