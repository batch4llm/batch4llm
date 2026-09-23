from pathlib import Path
from typing import Annotated

import typer
from alembic import command
from alembic.config import Config
from pydantic import AliasChoices, Field, PostgresDsn
from pydantic_settings import BaseSettings

import batch4llm.migrations as migrations_pkg

db_app = typer.Typer(help="Manage database schema migrations.", no_args_is_help=True)

SCRIPT_LOCATION = str(Path(migrations_pkg.__file__).parent)


class _DBSettings(BaseSettings):
    postgres_dsn: PostgresDsn = Field(
        validation_alias=AliasChoices("postgres_dsn", "database_url"),
    )


def _alembic_config() -> Config:
    config = Config()
    config.set_main_option("script_location", SCRIPT_LOCATION)
    config.set_main_option(
        "sqlalchemy.url", str(_DBSettings().postgres_dsn).replace("%", "%%")
    )
    return config


@db_app.command()
def upgrade(
    revision: Annotated[
        str, typer.Argument(help="Target revision (default: latest)")
    ] = "head",
):
    """Apply migrations up to REVISION."""
    command.upgrade(_alembic_config(), revision)


@db_app.command()
def downgrade(
    revision: Annotated[str, typer.Argument(help="Target revision")],
):
    """Revert migrations down to REVISION."""
    command.downgrade(_alembic_config(), revision)


@db_app.command()
def revision(
    message: Annotated[str, typer.Option("-m", "--message", help="Revision message")],
    autogenerate: Annotated[
        bool,
        typer.Option(
            "--autogenerate/--no-autogenerate",
            help="Detect model changes automatically",
        ),
    ] = True,
):
    """Generate a new migration script."""
    command.revision(_alembic_config(), message=message, autogenerate=autogenerate)


@db_app.command()
def current():
    """Show the current database revision."""
    command.current(_alembic_config(), verbose=True)


@db_app.command()
def history():
    """List all migrations."""
    command.history(_alembic_config(), verbose=True)


@db_app.command()
def stamp(
    revision: Annotated[str, typer.Argument(help="Revision to stamp as applied")],
):
    """Mark REVISION as applied without running any migrations."""
    command.stamp(_alembic_config(), revision)
