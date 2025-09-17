import typer

from pathlib import Path
from rich import print as rprint
from typing_extensions import Annotated


def register_workspace_initialize(app: typer.Typer):
    @app.command(name="initialize")
    def workspace_initialize(
        name: str,
        out_path: Path | None = None,
        force: Annotated[
            bool, typer.Option("--force", help="Overwrite existing workspace")
        ] = False,
    ) -> None:
        """Create a folder to store data related to a workspace."""
        from ow.workspace.tools import create_workspace

        try:
            workspace = create_workspace(name=name, out_path=out_path, force=force)
            rprint(f"✅ Workspace initialized at: {workspace.workspace_path}")
        except FileExistsError as e:
            rprint(f"⚠️  [yellow]Workspace: `{name}` already exists.[/yellow]")
            rprint("Use [cyan]--force[/cyan] to overwrite, or edit the existing file.")
            _ = typer.Exit()
        except:
            rprint("⚠️  [yellow]Unable to create workspace directory[/yellow]")
            _ = typer.Exit()

    _ = app.command(name="init")(workspace_initialize)

    return workspace_initialize
