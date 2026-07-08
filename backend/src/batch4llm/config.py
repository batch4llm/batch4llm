from pydantic_settings import BaseSettings
from pydantic import (
    AliasChoices,
    Field,
    PostgresDsn,
    RedisDsn,
)


class ServiceSettings(BaseSettings):
    postgres_dsn: PostgresDsn = Field(
        validation_alias=AliasChoices("postgres_dsn", "database_url"),
    )

    redis_dsn: RedisDsn = Field(
        validation_alias=AliasChoices("redis_dsn", "redis_url"),
    )

    minio_endpoint: str = Field(validation_alias=AliasChoices("MINIO_ENDPOINT"))
    minio_access_key: str = Field(validation_alias=AliasChoices("MINIO_ACCESS_KEY"))
    minio_secret_key: str = Field(validation_alias=AliasChoices("MINIO_SECRET_KEY"))
    minio_bucket: str = Field(validation_alias=AliasChoices("MINIO_BUCKET"))
    minio_secure: bool = Field(validation_alias=AliasChoices("MINIO_SECURE"))
    minio_public_url: str | None = Field(
        default=None, validation_alias=AliasChoices("MINIO_PUBLIC_URL")
    )

    model_sync_interval_minutes: int = Field(
        default=60, validation_alias=AliasChoices("MODEL_SYNC_INTERVAL_MINUTES")
    )


class AppSettings(BaseSettings):
    secure_cookies: bool = Field(validation_alias=AliasChoices("SECURE_COOKIES"))
    access_token_expire_minutes: int = Field(
        validation_alias=AliasChoices("ACCESS_TOKEN_EXPIRE_MINUTES")
    )
    auth_required: bool = Field(validation_alias=AliasChoices("AUTH_REQUIRED"))
