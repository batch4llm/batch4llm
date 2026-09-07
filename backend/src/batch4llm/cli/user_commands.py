import os
import typer
from typing import Annotated

from .deps import get_login_service, get_user_service

user_app = typer.Typer(help="Manage users.", no_args_is_help=True)


@user_app.command()
def create(
    username: Annotated[str, typer.Argument(help="Username (3–10 characters)")],
    password: Annotated[str, typer.Argument(help="Password (min. 6 characters)")],
    admin: Annotated[
        bool, typer.Option("--admin", help="Grant admin privileges")
    ] = False,
):
    """Create a new user."""
    try:
        get_login_service().register_user(
            username, password, is_admin=True if admin else None
        )
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


@user_app.command(name="ensure-admin")
def ensure_admin():
    """Create a bootstrap admin from ADMIN_USERNAME/ADMIN_PASSWORD env vars.

    No-op if both are unset, or if a user with that username already exists
    (existing accounts, including their passwords, are never modified)."""
    username = os.environ.get("ADMIN_USERNAME")
    password = os.environ.get("ADMIN_PASSWORD")

    if not username and not password:
        typer.echo("ADMIN_USERNAME/ADMIN_PASSWORD not set, skipping admin bootstrap.")
        return
    if not username or not password:
        typer.echo(
            "Error: ADMIN_USERNAME and ADMIN_PASSWORD must both be set to bootstrap "
            "an admin account.",
            err=True,
        )
        raise typer.Exit(1)

    try:
        created = get_login_service().ensure_bootstrap_admin(username, password)
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

    if created:
        typer.echo(f"Created admin '{username}'.")
    else:
        typer.echo(f"Admin '{username}' already exists, skipping bootstrap.")


@user_app.command()
def reset_password(
    username: Annotated[str, typer.Argument(help="Username")],
    password: Annotated[str, typer.Argument(help="New password (min. 6 characters)")],
):
    """Set a new password for a user."""
    try:
        get_login_service().reset_password(username, password)
        typer.echo(f"Password for '{username}' updated.")
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


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
