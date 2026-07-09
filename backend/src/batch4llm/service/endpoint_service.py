from ..manager.database import Database
from ..manager.endpoint_manager import EndpointManager
from ..manager.llm_client.models.engine_health_model import EngineHealth
from ..manager.price_calculator import get_model_pricing


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
        endpoint_internal = self.db.endpoints.get(ep["id"], user_id, show_api=True)
        self.sync_models(endpoint_internal)
        return ep

    def sync_models(self, endpoint: dict) -> None:
        """Fetch an endpoint's available models, persist their pricing, and record
        the endpoint's health. `endpoint` must be an internal dict (with token/url),
        e.g. from `db.endpoints.get(..., show_api=True)`."""
        try:
            model_names = self.endpoint_manager.get_models(endpoint)
        except Exception as e:
            self.db.endpoints.update_health(
                endpoint["id"], is_healthy=False, error=str(e)
            )
            return

        self.db.endpoints.update_health(endpoint["id"], is_healthy=True, error=None)
        for model_name in model_names:
            pricing = get_model_pricing(endpoint["provider"], model_name)
            input_cost, output_cost = pricing if pricing else (None, None)
            self.db.endpoint_models.upsert(
                endpoint["id"], model_name, input_cost, output_cost
            )

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

    def list(self, user_id: int, archived: bool | None = None) -> list[dict]:
        return self.db.endpoints.list(user_id, archived)

    def set_archived(self, endpoint_id: int, user_id: int, archived: bool) -> dict:
        return self.db.endpoints.set_archived(endpoint_id, user_id, archived)

    def delete(self, endpoint_id: int, user_id: int) -> dict:
        endpoint = self.db.endpoints.delete(endpoint_id, user_id)
        return endpoint
