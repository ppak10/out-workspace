import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from ow.workspace.tools.list import list_workspaces


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

    @patch("ow.workspace.tools.list.get_project_root")
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
