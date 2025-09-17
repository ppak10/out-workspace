import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from ow.workspace.model import Workspace
from ow.workspace.tools import create_workspace, list_workspaces


class TestListWorkspaces:
    def test_list_workspaces_with_existing_directories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            out_path = Path(temp_dir)

            # Create some workspace directories
            (out_path / "workspace1").mkdir()
            (out_path / "workspace2").mkdir()
            (out_path / "workspace3").mkdir()

            # Create a file (should be ignored)
            (out_path / "not_a_workspace.txt").touch()

            result = list_workspaces(out_path)

            assert set(result) == {"workspace1", "workspace2", "workspace3"}

    def test_list_workspaces_empty_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            out_path = Path(temp_dir)

            result = list_workspaces(out_path)

            assert result == []

    def test_list_workspaces_nonexistent_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            out_path = Path(temp_dir) / "nonexistent"

            result = list_workspaces(out_path)

            # Should create the directory and return empty list
            assert out_path.exists()
            assert result == []

    @patch("ow.workspace.tools.get_project_root")
    def test_list_workspaces_default_path(self, mock_get_project_root):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            out_path = project_root / "out"
            mock_get_project_root.return_value = project_root

            # Create workspace directories
            out_path.mkdir()
            (out_path / "default_workspace").mkdir()

            result = list_workspaces()

            assert result == ["default_workspace"]

    def test_list_workspaces_path_is_file_raises_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "file.txt"
            file_path.touch()

            with pytest.raises(FileNotFoundError):
                list_workspaces(file_path)


class TestCreateWorkspace:
    def test_create_workspace_basic(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            out_path = Path(temp_dir)
            workspace_name = "test_workspace"

            workspace = create_workspace(out_path, workspace_name)

            assert isinstance(workspace, Workspace)
            assert workspace.name == workspace_name
            assert workspace.out_path == out_path
            assert workspace.workspace_path == out_path / workspace_name

    def test_create_workspace_creates_out_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            out_path = Path(temp_dir) / "new_out"
            workspace_name = "test_workspace"

            assert not out_path.exists()

            workspace = create_workspace(out_path, workspace_name)

            assert out_path.exists()
            assert out_path.is_dir()
            assert isinstance(workspace, Workspace)

    def test_create_workspace_existing_workspace_without_force_raises_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            out_path = Path(temp_dir)
            workspace_name = "existing_workspace"
            workspace_path = out_path / workspace_name

            # Create existing workspace directory
            workspace_path.mkdir(parents=True)

            with pytest.raises(FileExistsError, match="Workspace already exists"):
                create_workspace(out_path, workspace_name)

    def test_create_workspace_existing_workspace_with_force_succeeds(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            out_path = Path(temp_dir)
            workspace_name = "existing_workspace"
            workspace_path = out_path / workspace_name

            # Create existing workspace directory
            workspace_path.mkdir(parents=True)

            workspace = create_workspace(out_path, workspace_name, force=True)

            assert isinstance(workspace, Workspace)
            assert workspace.name == workspace_name

    def test_create_workspace_name_sanitization(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            out_path = Path(temp_dir)
            workspace_name = "test workspace with spaces"

            workspace = create_workspace(out_path, workspace_name)

            # The Workspace model should sanitize the name
            assert workspace.name == "test_workspace_with_spaces"
