from celery import Celery
from batch4llm.config import ServiceSettings

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
}
app.conf.task_track_started = True

app.autodiscover_tasks(["batch4llm.celery.tasks"])
