import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch

from ow.workspace.model import Workspace


class TestWorkspace:

    def test_workspace_creation_with_basic_name(self):
        workspace = Workspace(name="test_workspace")
        assert workspace.name == "test_workspace"
        assert workspace.out_path is not None
        assert workspace.workspace_path is not None

    def test_name_sanitization_spaces(self):
        workspace = Workspace(name="test workspace")
        assert workspace.name == "test_workspace"

    def test_name_sanitization_special_characters(self):
        workspace = Workspace(name='test<>:"/\\|?*workspace')
        assert workspace.name == "testworkspace"

    def test_name_sanitization_control_characters(self):
        workspace = Workspace(name="test\x00\x01workspace")
        assert workspace.name == "testworkspace"

    def test_name_truncation(self):
        long_name = "a" * 300
        workspace = Workspace(name=long_name)
        assert len(workspace.name) == 255
        assert workspace.name == "a" * 255

    @patch("ow.workspace.model.get_project_root")
    def test_path_population_default(self, mock_get_project_root):
        mock_root = Path("/mock/project/root")
        mock_get_project_root.return_value = mock_root

        workspace = Workspace(name="test")

        assert workspace.out_path == mock_root / "out"
        assert workspace.workspace_path == mock_root / "out" / "test"

    def test_path_population_with_custom_out_path(self):
        custom_out_path = Path("/custom/out")
        workspace = Workspace(name="test", out_path=custom_out_path)

        assert workspace.out_path == custom_out_path
        assert workspace.workspace_path == custom_out_path / "test"

    def test_path_population_with_both_custom_paths(self):
        custom_out_path = Path("/custom/out")
        custom_workspace_path = Path("/custom/workspace")
        workspace = Workspace(
            name="test", out_path=custom_out_path, workspace_path=custom_workspace_path
        )

        assert workspace.out_path == custom_out_path
        assert workspace.workspace_path == custom_workspace_path

    def test_save_default_path(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace_path = Path(tmp_dir) / "test_workspace"
            workspace = Workspace(name="test", workspace_path=workspace_path)

            saved_path = workspace.save()
            expected_path = workspace_path / "workspace.json"

            assert saved_path == expected_path
            assert expected_path.exists()

            # Verify content
            content = json.loads(expected_path.read_text())
            assert content["name"] == "test"

    def test_save_custom_path(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            custom_path = Path(tmp_dir) / "custom_config.json"
            workspace = Workspace(name="test")

            saved_path = workspace.save(custom_path)

            assert saved_path == custom_path
            assert custom_path.exists()

            # Verify content
            content = json.loads(custom_path.read_text())
            assert content["name"] == "test"

    def test_save_creates_parent_directories(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            nested_path = Path(tmp_dir) / "nested" / "directory" / "config.json"
            workspace = Workspace(name="test")

            saved_path = workspace.save(nested_path)

            assert saved_path == nested_path
            assert nested_path.exists()
            assert nested_path.parent.exists()

    def test_save_without_workspace_path_raises_error(self):
        workspace = Workspace(name="test", workspace_path=None)
        workspace.workspace_path = None  # Explicitly set to None after validation

        with pytest.raises(ValueError, match="workspace_path must be set"):
            workspace.save()

    def test_load_existing_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "config.json"
            workspace_data = {
                "name": "loaded_workspace",
                "out_path": "/some/path",
                "workspace_path": "/some/workspace/path",
            }
            config_path.write_text(json.dumps(workspace_data))

            loaded_workspace = Workspace.load(config_path)

            assert loaded_workspace.name == "loaded_workspace"
            assert str(loaded_workspace.out_path) == "/some/path"
            assert str(loaded_workspace.workspace_path) == "/some/workspace/path"

    def test_load_nonexistent_file(self):
        nonexistent_path = Path("/nonexistent/config.json")

        with pytest.raises(FileNotFoundError, match="Config file not found"):
            Workspace.load(nonexistent_path)

    def test_round_trip_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            original_workspace = Workspace(
                name="round_trip_test",
                out_path=Path("/original/out"),
                workspace_path=Path("/original/workspace"),
            )

            config_path = Path(tmp_dir) / "config.json"
            original_workspace.save(config_path)

            loaded_workspace = Workspace.load(config_path)

            assert loaded_workspace.name == original_workspace.name
            assert loaded_workspace.out_path == original_workspace.out_path
            assert loaded_workspace.workspace_path == original_workspace.workspace_path
