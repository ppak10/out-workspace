import os

from pathlib import Path

from ow.workspace.model import Workspace
from ow.workspace.utils import get_project_root


def list_workspaces(out_path: Path | None = None) -> list[str] | None:
    """
    Lists workspace directories within out_path
    """
    if out_path is None:
        out_path = get_project_root() / "out"

    if not out_path.exists():
        os.makedirs(out_path)

    if not out_path.is_dir():
        raise FileNotFoundError

    return [
        workspace_dir.name
        for workspace_dir in out_path.iterdir()
        if workspace_dir.is_dir()
    ]


def list_workspace_subfolders(
    name: str, out_path: Path | None = None
) -> list[str] | None:
    """
    Lists subfolders within a workspace.
    """
    if out_path is None:
        out_path = get_project_root() / "out"

    if not out_path.exists() or not out_path.is_dir():
        raise FileNotFoundError

    workspace_dict_path = out_path / name / "workspace.json"

    if not workspace_dict_path.exists():
        raise FileNotFoundError

    workspace = Workspace.load(workspace_dict_path)

    return workspace.subfolders


def list_workspace_subfolder_content(
    name: str, subfolder: str, out_path: Path | None = None
) -> list[str] | None:
    """
    Lists the contents within a workspace subfolder.
    """

    if out_path is None:
        out_path = get_project_root() / "out"

    if not out_path.exists() or not out_path.is_dir():
        raise FileNotFoundError

    subfolder_path = out_path / name / subfolder

    return [content.name for content in subfolder_path.iterdir()]
