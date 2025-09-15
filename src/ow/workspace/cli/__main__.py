import typer

app = typer.Typer(
    name="workspace",
    help="Create and list workspaces",
    add_completion=False,
    no_args_is_help=True,
)
