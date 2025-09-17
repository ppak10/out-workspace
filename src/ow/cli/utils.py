import typer

from pathlib import Path
from rich import print as rprint

from .options import WorkspaceOption


def get_workspace_path(
    workspace: WorkspaceOption, config_file: str = "workspace.json"
) -> Path:
    """
    Checks for workspace config file in current directory or throws error.
    """
    if workspace is not None:
        # Get workspace path from name.
        from ow.workspace.utils import get_project_root

        project_root = get_project_root()
        workspace_dir = project_root / "out" / workspace

    else:
        # Check for workspace config file in current directory
        workspace_dir = Path.cwd()

    workspace_config_path = workspace_dir / config_file

    if not workspace_config_path.exists():
        rprint(
            f"❌ [red]This is not a valid workspace folder. `{workspace_config_path}` not found.[/red]"
        )
        raise typer.Exit(code=1)

    return workspace_dir
