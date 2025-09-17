import os

from pathlib import Path

from .model import Workspace
from .utils import get_project_root


def list_workspaces(out_path: Path | None = None) -> list[str] | None:
    """
    Lists workspace directories within out_path
    """
    if out_path is None:
        project_root = get_project_root()
        out_path = project_root / "out"

    if not out_path.exists():
        os.makedirs(out_path)

    if not out_path.is_dir():
        raise FileNotFoundError

    return [
        workspace_dir.name
        for workspace_dir in out_path.iterdir()
        if workspace_dir.is_dir()
    ]


def create_workspace(
    name: str,
    out_path: Path | None = None,
    force: bool = False,
    **kwargs,
) -> Workspace:
    """
    Create Workspace class object and folder.
    """

    # Use the out_path if provided, otherwise default to package out_path.
    if out_path is None:
        out_path = get_project_root() / "out"

    # Create the `out` directory if it doesn't exist.
    out_path.mkdir(exist_ok=True)

    workspace_path = out_path / name

    if workspace_path.exists() and not force:
        raise FileExistsError("Workspace already exists")

    workspace = Workspace(name=name, out_path=out_path, **kwargs)
    workspace.save()

    return workspace
