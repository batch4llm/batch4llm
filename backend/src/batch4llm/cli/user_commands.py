import typer
from typing import Annotated
from pydantic import Field, PostgresDsn, AliasChoices
from pydantic_settings import BaseSettings

from batch4llm.manager.database import Database
from batch4llm.service.login_service import LoginService

user_app = typer.Typer(help="Manage users.", no_args_is_help=True)


class _CLISettings(BaseSettings):
    postgres_dsn: PostgresDsn = Field(
        validation_alias=AliasChoices("postgres_dsn", "database_url"),
    )


def _get_login_service() -> LoginService:
    settings = _CLISettings()
    db = Database(str(settings.postgres_dsn))
    return LoginService(db, secret_key="", algorithm="HS256", token_expire_minutes=0)


@user_app.command()
def create(
    username: Annotated[str, typer.Argument(help="Username (3–10 characters)")],
    password: Annotated[str, typer.Argument(help="Password (min. 6 characters)")],
    admin: Annotated[bool, typer.Option("--admin", help="Grant admin privileges")] = False,
):
    """Create a new user."""
    login_service = _get_login_service()
    try:
        login_service.register_user(username, password, is_admin=True if admin else None)
        role = "admin" if admin else "user"
        typer.echo(f"Created {role} '{username}'.")
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
