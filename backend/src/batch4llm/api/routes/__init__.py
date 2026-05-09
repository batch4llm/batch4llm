from fastapi import APIRouter
from .file_routes import build_file_router
from .batch_routes import build_batch_router
from .endpoint_routes import build_endpoint_router
from .pipeline_routes import build_pipeline_router
from .export_routes import build_export_router
from .price_routes import build_price_router
from .prompt_routes import build_prompt_router
from .authentication_routes import build_authentication_router
from .admin_routes import build_admin_router


def build_router(
    file_service,
    batch_service,
    endpoint_service,
    export_service,
    prompt_service,
    login_service,
    jwt_authenticator,
    user_service,
    price_service,
):
    router = APIRouter()
    router.include_router(build_file_router(file_service, jwt_authenticator))
    router.include_router(build_batch_router(batch_service, jwt_authenticator))
    router.include_router(build_endpoint_router(endpoint_service, jwt_authenticator))
    router.include_router(build_pipeline_router(batch_service))
    router.include_router(build_export_router(export_service, jwt_authenticator))
    router.include_router(build_prompt_router(prompt_service, jwt_authenticator))
    router.include_router(build_authentication_router(login_service, jwt_authenticator))
    router.include_router(build_price_router(price_service, jwt_authenticator))
    router.include_router(build_admin_router(user_service, jwt_authenticator))
    return router
