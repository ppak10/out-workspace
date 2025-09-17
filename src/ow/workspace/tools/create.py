from pathlib import Path

from ow.workspace.model import Workspace
from ow.workspace.utils import get_project_root


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


def create_workspace_subfolder(
    name: str,
    subfolder: str,
    out_path: Path | None = None,
    force: bool = False,
    **kwargs,
) -> Workspace:
    """
    Create a subfolder within a Workspace and register it in workspace.json.
    """

    # Use the out_path if provided, otherwise default to package out_path.
    if out_path is None:
        out_path = get_project_root() / "out"

    if not out_path.exists() or not out_path.is_dir():
        raise FileNotFoundError

    workspace_dict_path = out_path / name / "workspace.json"

    if not workspace_dict_path.exists():
        raise FileNotFoundError

    subfolder_path = out_path / name / subfolder

    if subfolder_path.exists() and not force:
        raise FileExistsError("Workspace subfolder already exists")

    workspace = Workspace.load(workspace_dict_path)
    workspace.add_subfolder(subfolder)

    return workspace
