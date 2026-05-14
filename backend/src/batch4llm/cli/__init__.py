import typer
from .user_commands import user_app
from .group_commands import group_app

app = typer.Typer(name="batch4llm", help="batch4llm admin CLI", no_args_is_help=True)
app.add_typer(user_app, name="user")
app.add_typer(group_app, name="group")
