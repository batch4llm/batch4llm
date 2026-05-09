from batch4llm.manager.llm_client.models.engine_health_model import EngineHealth
from batch4llm.manager.llm_client.client_manager import ClientManager


class EndpointManager:
    def __init__(self, client_manager: ClientManager):
        self.client_manager = client_manager

    def get_models(self, endpoint) -> list[str]:
        return self.client_manager.endpoint_models(endpoint)

    def get_health(self, endpoint) -> EngineHealth:
        return self.client_manager.endpoint_health(endpoint)
