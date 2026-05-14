import typer
from typing import Annotated

from .deps import get_login_service, get_user_service

user_app = typer.Typer(help="Manage users.", no_args_is_help=True)


@user_app.command()
def create(
    username: Annotated[str, typer.Argument(help="Username (3–10 characters)")],
    password: Annotated[str, typer.Argument(help="Password (min. 6 characters)")],
    admin: Annotated[bool, typer.Option("--admin", help="Grant admin privileges")] = False,
):
    """Create a new user."""
    try:
        get_login_service().register_user(username, password, is_admin=True if admin else None)
        role = "admin" if admin else "user"
        typer.echo(f"Created {role} '{username}'.")
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@user_app.command(name="list")
def list_users():
    """List all users."""
    users = get_user_service().get_users()
    if not users:
        typer.echo("No users found.")
        return
    for u in users:
        admin_flag = " [admin]" if u.get("is_admin") else ""
        group = f"  group={u['group_id']}" if u.get("group_id") else ""
        typer.echo(f"{u['username']}{admin_flag}{group}")


@user_app.command()
def set_group(
    username: Annotated[str, typer.Argument(help="Username")],
    group_id: Annotated[int, typer.Argument(help="Group ID")],
):
    """Assign a user to a group."""
    try:
        get_user_service().set_user_group(username, group_id)
        typer.echo(f"Assigned '{username}' to group {group_id}.")
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
