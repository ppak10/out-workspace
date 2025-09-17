import tempfile
from pathlib import Path

import pytest

from ow.workspace.model import Workspace
from ow.workspace.tools.create import create_workspace


class TestCreateWorkspace:
    def test_create_workspace_basic(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            out_path = Path(temp_dir)
            workspace_name = "test_workspace"

            workspace = create_workspace(workspace_name, out_path)

            assert isinstance(workspace, Workspace)
            assert workspace.name == workspace_name
            assert workspace.out_path == out_path
            assert workspace.workspace_path == out_path / workspace_name

    def test_create_workspace_creates_out_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            out_path = Path(temp_dir) / "new_out"
            workspace_name = "test_workspace"

            assert not out_path.exists()

            workspace = create_workspace(workspace_name, out_path)

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
                create_workspace(workspace_name, out_path)

    def test_create_workspace_existing_workspace_with_force_succeeds(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            out_path = Path(temp_dir)
            workspace_name = "existing_workspace"
            workspace_path = out_path / workspace_name

            # Create existing workspace directory
            workspace_path.mkdir(parents=True)

            workspace = create_workspace(workspace_name, out_path, force=True)

            assert isinstance(workspace, Workspace)
            assert workspace.name == workspace_name

    def test_create_workspace_name_sanitization(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            out_path = Path(temp_dir)
            workspace_name = "test workspace with spaces"

            workspace = create_workspace(workspace_name, out_path)

            # The Workspace model should sanitize the name
            assert workspace.name == "test_workspace_with_spaces"
