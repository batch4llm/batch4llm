from fastapi import APIRouter, Security

from batch4llm.api.models.model_models import ModelResponse
from batch4llm.service.model_service import ModelService
from batch4llm.service.jwt_authenticator import JWTAuthenticator


def build_model_router(
    model_service: ModelService, jwt_authenticator: JWTAuthenticator
):
    router = APIRouter(prefix="/models", tags=["Models"])

    @router.get("/", response_model=list[ModelResponse])
    def list_models(user=Security(jwt_authenticator)):
        return model_service.list_models(user["id"])

    return router
