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
        assert workspace.subfolders == []
        assert workspace.config_file == "workspace.json"

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

        with pytest.raises(FileNotFoundError, match="Workspace file not found"):
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

    def test_subfolders_default_value(self):
        workspace = Workspace(name="test")
        assert workspace.subfolders == []

    def test_subfolders_custom_value(self):
        workspace = Workspace(name="test", subfolders=["docs", "src", "tests"])
        assert workspace.subfolders == ["docs", "src", "tests"]

    def test_config_file_default_value(self):
        workspace = Workspace(name="test")
        assert workspace.config_file == "workspace.json"

    def test_config_file_custom_value(self):
        workspace = Workspace(name="test", config_file="custom.json")
        assert workspace.config_file == "custom.json"

    def test_create_subfolders_success(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace_path = Path(tmp_dir) / "test_workspace"
            workspace = Workspace(
                name="test",
                workspace_path=workspace_path,
                subfolders=["docs", "src", "tests"],
            )

            created_paths = workspace.create_subfolders()

            assert len(created_paths) == 3
            assert workspace_path / "docs" in created_paths
            assert workspace_path / "src" in created_paths
            assert workspace_path / "tests" in created_paths

            # Verify directories were actually created
            assert (workspace_path / "docs").exists()
            assert (workspace_path / "src").exists()
            assert (workspace_path / "tests").exists()

    def test_create_subfolders_empty_list(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace_path = Path(tmp_dir) / "test_workspace"
            workspace = Workspace(name="test", workspace_path=workspace_path)

            created_paths = workspace.create_subfolders()

            assert created_paths == []

    def test_create_subfolders_without_workspace_path(self):
        workspace = Workspace(name="test", workspace_path=None, subfolders=["docs"])
        workspace.workspace_path = None  # Explicitly set to None after validation

        with pytest.raises(
            ValueError, match="workspace_path must be set before creating subfolders"
        ):
            workspace.create_subfolders()

    def test_create_subfolders_with_nested_paths(self):
        # Note: create_subfolders still supports nested paths for existing configurations
        # but add_subfolder now prevents creating new nested paths
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace_path = Path(tmp_dir) / "test_workspace"
            workspace = Workspace(
                name="test",
                workspace_path=workspace_path,
                subfolders=["src/main", "tests/unit"],
            )

            created_paths = workspace.create_subfolders()

            assert len(created_paths) == 2
            assert (workspace_path / "src/main").exists()
            assert (workspace_path / "tests/unit").exists()

    def test_add_subfolder_success(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace_path = Path(tmp_dir) / "test_workspace"
            workspace = Workspace(name="test", workspace_path=workspace_path)

            folder_path = workspace.add_subfolder("new_folder")

            assert folder_path == workspace_path / "new_folder"
            assert folder_path.exists()
            assert "new_folder" in workspace.subfolders

    def test_add_subfolder_with_spaces(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace_path = Path(tmp_dir) / "test_workspace"
            workspace = Workspace(name="test", workspace_path=workspace_path)

            folder_path = workspace.add_subfolder("my folder")

            assert folder_path == workspace_path / "my_folder"
            assert folder_path.exists()
            assert "my_folder" in workspace.subfolders

    def test_add_subfolder_with_special_characters(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace_path = Path(tmp_dir) / "test_workspace"
            workspace = Workspace(name="test", workspace_path=workspace_path)

            # Test special characters excluding path separators (/ and \)
            folder_path = workspace.add_subfolder('folder<>:"|?*')

            assert folder_path == workspace_path / "folder"
            assert folder_path.exists()
            assert "folder" in workspace.subfolders

    def test_add_subfolder_duplicate_name(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace_path = Path(tmp_dir) / "test_workspace"
            workspace = Workspace(
                name="test", workspace_path=workspace_path, subfolders=["existing"]
            )

            folder_path = workspace.add_subfolder("existing")

            assert folder_path == workspace_path / "existing"
            assert folder_path.exists()
            # Should not duplicate in the list
            assert workspace.subfolders.count("existing") == 1

    def test_add_subfolder_without_workspace_path(self):
        workspace = Workspace(name="test", workspace_path=None)
        workspace.workspace_path = None  # Explicitly set to None after validation

        with pytest.raises(
            ValueError, match="workspace_path must be set before adding subfolders"
        ):
            workspace.add_subfolder("test_folder")

    def test_add_subfolder_nested_path_raises_error(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace_path = Path(tmp_dir) / "test_workspace"
            workspace = Workspace(name="test", workspace_path=workspace_path)

            with pytest.raises(
                ValueError, match="Nested subfolder paths are not allowed"
            ):
                workspace.add_subfolder("src/components")

    def test_add_subfolder_backslash_path_raises_error(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace_path = Path(tmp_dir) / "test_workspace"
            workspace = Workspace(name="test", workspace_path=workspace_path)

            with pytest.raises(
                ValueError, match="Nested subfolder paths are not allowed"
            ):
                workspace.add_subfolder("src\\components")

    def test_add_subfolder_long_name_truncation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace_path = Path(tmp_dir) / "test_workspace"
            workspace = Workspace(name="test", workspace_path=workspace_path)

            long_name = "a" * 300
            folder_path = workspace.add_subfolder(long_name)
            expected_name = "a" * 255

            assert folder_path == workspace_path / expected_name
            assert folder_path.exists()
            assert expected_name in workspace.subfolders
