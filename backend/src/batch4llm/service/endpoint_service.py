from ..manager.database import Database
from ..manager.endpoint_manager import EndpointManager
from ..manager.llm_client.models.engine_health_model import EngineHealth


class EndpointService:
    def __init__(self, db: Database, endpoint_manager: EndpointManager):
        self.db = db
        self.endpoint_manager = endpoint_manager

    def add(
        self,
        name: str,
        client: str,
        provider: str,
        user_id: int,
        url: str | None = None,
        token: str | None = None,
    ) -> dict:
        ep = self.db.endpoints.add(name, client, provider, user_id, url, token)
        return ep

    def test(
        self,
        name: str,
        client: str,
        provider: str,
        url: str | None = None,
        token: str | None = None,
    ) -> EngineHealth:
        temp_endpoint = {
            "name": name,
            "client": client,
            "provider": provider,
            "url": url,
            "token": token,
        }
        return self.endpoint_manager.get_health(temp_endpoint)

    def get(self, endpoint_id: int, user_id: int, show_api=False) -> dict:
        endpoint = self.db.endpoints.get(endpoint_id, user_id, show_api)
        return endpoint

    def health(self, endpoint_id: int, user_id: int) -> bool:
        endpoint = self.db.endpoints.get(endpoint_id, user_id, show_api=True)
        health = self.endpoint_manager.get_health(endpoint)
        return health.healthy

    def models(self, endpoint_id: int, user_id: int) -> list[str]:
        endpoint = self.db.endpoints.get(endpoint_id, user_id, show_api=True)
        return self.endpoint_manager.get_models(endpoint)

    def list(self, user_id: int) -> list[dict]:
        return self.db.endpoints.list(user_id)

    def delete(self, endpoint_id: int, user_id: int) -> dict:
        endpoint = self.db.endpoints.delete(endpoint_id, user_id)
        return endpoint
