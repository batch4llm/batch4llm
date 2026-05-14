import typer
from typing import Annotated

from .deps import get_user_service

group_app = typer.Typer(help="Manage groups.", no_args_is_help=True)


@group_app.command()
def add(
    name: Annotated[str, typer.Argument(help="Group name")],
):
    """Create a new group."""
    try:
        group = get_user_service().add_group(name)
        typer.echo(f"Created group '{group['name']}' (id={group['id']}).")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@group_app.command(name="list")
def list_groups():
    """List all groups."""
    groups = get_user_service().get_groups()
    if not groups:
        typer.echo("No groups found.")
        return
    for g in groups:
        typer.echo(f"{g['id']}  {g['name']}")
