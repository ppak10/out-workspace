import typer

from typing_extensions import Annotated
from pathlib import Path
from rich import print as rprint

from ow.mcp.install import install


def register_mcp_install(app: typer.Typer):
    @app.command(name="install")
    def mcp_install(
        client: Annotated[
            str,
            typer.Option("--client", help="Target client to install for."),
        ] = "claude-code",
        include_agent: Annotated[bool, typer.Option("--include-agent")] = True,
        project_path: Annotated[str | None, typer.Option("--project-path")] = None,
    ) -> None:
        import ow

        # Determine project root path
        if project_path:
            ow_path = Path(project_path)
        else:
            # Path(ow.__file__) example:
            # /GitHub/additive-manufacturing-agent/.venv/lib/python3.13/site-packages/ow
            # Going up 5 levels to get to the project root
            ow_path = Path(ow.__file__).parents[5]

        rprint(
            f"[bold green]Using `out-workspace` packaged under project path:[/bold green] {ow_path}"
        )

        install(ow_path, client=client, include_agent=include_agent)

    _ = app.command(name="install")(mcp_install)
    return mcp_install
