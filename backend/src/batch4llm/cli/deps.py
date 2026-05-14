from pydantic import Field, PostgresDsn, AliasChoices
from pydantic_settings import BaseSettings

from batch4llm.manager.database import Database
from batch4llm.service.login_service import LoginService
from batch4llm.service.user_service import UserService


class _CLISettings(BaseSettings):
    postgres_dsn: PostgresDsn = Field(
        validation_alias=AliasChoices("postgres_dsn", "database_url"),
    )


def get_db() -> Database:
    return Database(str(_CLISettings().postgres_dsn))


def get_login_service() -> LoginService:
    return LoginService(
        get_db(), secret_key="", algorithm="HS256", token_expire_minutes=0
    )


def get_user_service() -> UserService:
    return UserService(get_db())
