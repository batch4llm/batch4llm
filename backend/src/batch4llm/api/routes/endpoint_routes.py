from fastapi import APIRouter, HTTPException, status, Security

from batch4llm.api.models.endpoint_models import EndpointRequest, EndpointResponse
from batch4llm.core.exceptions import NameAlreadyExistsError
from batch4llm.service.endpoint_service import EndpointService
from batch4llm.service.jwt_authenticator import JWTAuthenticator


def build_endpoint_router(
    endpoint_service: EndpointService, jwt_authenticator: JWTAuthenticator
):
    router = APIRouter(prefix="/endpoints", tags=["Endpoints"])

    @router.post("/add", response_model=EndpointResponse)
    def add_endpoint(ep: EndpointRequest, user=Security(jwt_authenticator)):
        try:
            return endpoint_service.add(
                ep.name, ep.client, ep.provider, user["id"], ep.url, ep.token
            )
        except NameAlreadyExistsError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    @router.post("/test")
    def test_endpoint(ep: EndpointRequest, user=Security(jwt_authenticator)):
        endpoint_health = endpoint_service.test(
            ep.name, ep.client, ep.provider, ep.url, ep.token
        )
        if endpoint_health.healthy:
            return {
                "success": True,
                "name": ep.name,
            }
        else:
            return {
                "success": False,
                "error": endpoint_health.error,
            }

    @router.get("/", response_model=list[EndpointResponse])
    def list_endpoints(user=Security(jwt_authenticator)):
        return endpoint_service.list(user["id"])

    @router.get("/health/{endpoint_id}", response_model=bool)
    def get_endpoint_health(endpoint_id: int, user=Security(jwt_authenticator)):
        return endpoint_service.health(endpoint_id, user["id"])

    @router.get("/models/{endpoint_id}", response_model=list[str])
    def get_endpoint_models(endpoint_id: int, user=Security(jwt_authenticator)):
        return endpoint_service.models(endpoint_id, user["id"])

    @router.delete("/delete/{endpoint_id}", response_model=EndpointResponse)
    def delete_endpoint(endpoint_id: int, user=Security(jwt_authenticator)):
        return endpoint_service.delete(endpoint_id, user["id"])

    return router
