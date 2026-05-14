import typer
from .user_commands import user_app

app = typer.Typer(name="batch4llm", help="batch4llm admin CLI", no_args_is_help=True)
app.add_typer(user_app, name="user")
