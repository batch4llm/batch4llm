from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
import secrets
import string

from batch4llm.api.routes import build_router
from batch4llm.config import ServiceSettings, AppSettings
from batch4llm.manager.database import Database
from batch4llm.manager.endpoint_manager import EndpointManager
from batch4llm.manager.file_manager import FileManager
from batch4llm.manager.file_storage import MinIOStorage
from batch4llm.manager.llm_client.client_manager import ClientManager
from batch4llm.service.endpoint_service import EndpointService
from batch4llm.service.export_service import ExportService
from batch4llm.service.file_service import FileService
from batch4llm.service.batch_service import BatchService
from batch4llm.service.jwt_authenticator import JWTAuthenticator
from batch4llm.service.login_service import LoginService
from batch4llm.service.model_service import ModelService
from batch4llm.service.price_service import PriceService
from batch4llm.service.prompt_service import PromptService
from batch4llm.logger_config import setup_logging
from batch4llm.service.user_service import UserService
from batch4llm.manager.price_calculator import prefetch_pricing

setup_logging()
logger = logging.getLogger(__name__)


def generate_jwt_key(length=32):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


# configuration for jwt_authenticator
ALGORITHM = "HS256"
JWT_ENCRYPTION_KEY = generate_jwt_key()

service_settings = ServiceSettings()
app_settings = AppSettings()

if not app_settings.secure_cookies:
    logger.warning(
        "Secure cookie is disabled. This is only recommended for development."
    )


def create_app(required_user_auth=True) -> FastAPI:

    app = FastAPI(title="Batch4LLM")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        db = Database(str(service_settings.postgres_dsn))

        file_storage = MinIOStorage(
            service_settings.minio_endpoint,
            service_settings.minio_access_key,
            service_settings.minio_secret_key,
            service_settings.minio_bucket,
            secure=service_settings.minio_secure,
            public_url=service_settings.minio_public_url,
        )

        file_manager = FileManager(file_storage, db)
        client_manager = ClientManager()
        endpoint_manager = EndpointManager(client_manager)

        jwt_authenticator = JWTAuthenticator(
            JWT_ENCRYPTION_KEY,
            ALGORITHM,
            db,
            required_user_auth,
            app_settings.secure_cookies,
        )
        login_service = LoginService(
            db, JWT_ENCRYPTION_KEY, ALGORITHM, app_settings.access_token_expire_minutes
        )
        user_service = UserService(db)

        file_service = FileService(db, file_manager)
        endpoint_service = EndpointService(db, endpoint_manager)
        batch_service = BatchService(db, endpoint_service, file_service)
        export_service = ExportService(db)
        prompt_service = PromptService(db)
        price_service = PriceService(db, file_service)
        model_service = ModelService(db)

        file_manager.sync_storage_with_db()
        prefetch_pricing()

        router = build_router(
            file_service,
            batch_service,
            endpoint_service,
            export_service,
            prompt_service,
            login_service,
            jwt_authenticator,
            user_service,
            price_service,
            model_service,
        )
        app.include_router(router, prefix="/api")

        if not required_user_auth:
            try:
                login_service.register_user("localhost", "localhost")
            except ValueError:
                logger.warning("Failed to register user: localhost")

        yield

    app.router.lifespan_context = lifespan
    return app


app = create_app(app_settings.auth_required)
