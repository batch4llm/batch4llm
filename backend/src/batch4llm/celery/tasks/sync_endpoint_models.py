from batch4llm.celery.worker import app
from batch4llm.config import ServiceSettings
from batch4llm.manager.database import Database
from batch4llm.manager.endpoint_manager import EndpointManager
from batch4llm.manager.llm_client.client_manager import ClientManager
from batch4llm.service.endpoint_service import EndpointService

service_settings = ServiceSettings()
db = Database(service_settings.postgres_dsn)
endpoint_service = EndpointService(db, EndpointManager(ClientManager()))


@app.task
def sync_endpoint_models():
    for endpoint in db.worker.get_all_active_endpoints():
        endpoint_service.sync_models(endpoint)
