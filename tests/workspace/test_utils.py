from pathlib import Path
from unittest.mock import Mock, patch

from ow.workspace.utils import get_project_root


class TestGetProjectRoot:
    """Test cases for the get_project_root function."""

    @patch("importlib.util.find_spec")
    def test_get_project_root_local_development(self, mock_find_spec):
        """Test get_project_root in local development environment (src structure)."""
        # Mock spec for local development scenario
        mock_spec = Mock()
        mock_spec.origin = "/home/user/project/src/ow/__init__.py"
        mock_find_spec.return_value = mock_spec

        result = get_project_root()

        # Should return the project root (parent of src)
        expected = Path("/home/user/project")
        assert result == expected
        mock_find_spec.assert_called_once_with("ow")

    @patch("importlib.util.find_spec")
    def test_get_project_root_pypi_install_default_parents(self, mock_find_spec):
        """Test get_project_root with PyPI installation using default parents_index."""
        # Mock spec for PyPI installation scenario
        mock_spec = Mock()
        mock_spec.origin = (
            "/home/user/.venv/lib/python3.13/site-packages/ow/__init__.py"
        )
        mock_find_spec.return_value = mock_spec

        result = get_project_root()

        # Should return 4 levels up from the package path
        # package_path: /home/user/.venv/lib/python3.13/site-packages/ow
        # parents[4]: /home (assuming this structure)
        package_path = Path("/home/user/.venv/lib/python3.13/site-packages/ow")
        expected = package_path.parents[4]  # This would be /home
        assert result == expected

    @patch("importlib.util.find_spec")
    def test_get_project_root_pypi_install_custom_parents(self, mock_find_spec):
        """Test get_project_root with PyPI installation using custom parents_index."""
        # Mock spec for PyPI installation scenario
        mock_spec = Mock()
        mock_spec.origin = (
            "/home/user/.venv/lib/python3.13/site-packages/ow/__init__.py"
        )
        mock_find_spec.return_value = mock_spec

        result = get_project_root(parents_index=2)

        # Should return 2 levels up from the package path
        package_path = Path("/home/user/.venv/lib/python3.13/site-packages/ow")
        expected = package_path.parents[2]  # This would be /home/user/.venv
        assert result == expected

    @patch("importlib.util.find_spec")
    def test_get_project_root_spec_none(self, mock_find_spec):
        """Test get_project_root when spec is None."""
        mock_find_spec.return_value = None

        result = get_project_root()

        # Should fall back to current working directory
        assert result == Path.cwd()

    @patch("importlib.util.find_spec")
    def test_get_project_root_spec_no_origin(self, mock_find_spec):
        """Test get_project_root when spec has no origin."""
        mock_spec = Mock()
        mock_spec.origin = None
        mock_find_spec.return_value = mock_spec

        result = get_project_root()

        # Should fall back to current working directory
        assert result == Path.cwd()

    @patch("importlib.util.find_spec")
    def test_get_project_root_import_error(self, mock_find_spec):
        """Test get_project_root when ImportError is raised."""
        mock_find_spec.side_effect = ImportError("Module not found")

        result = get_project_root()

        # Should fall back to current working directory
        assert result == Path.cwd()

    def test_get_project_root_returns_path_object(self):
        """Test that get_project_root always returns a Path object."""
        result = get_project_root()
        assert isinstance(result, Path)

    @patch("importlib.util.find_spec")
    @patch("pathlib.Path.cwd")
    def test_get_project_root_fallback_to_cwd(self, mock_cwd, mock_find_spec):
        """Test that get_project_root falls back to current working directory."""
        mock_find_spec.side_effect = ImportError()
        mock_cwd.return_value = Path("/fallback/directory")

        result = get_project_root()

        assert result == Path("/fallback/directory")
        mock_cwd.assert_called_once()
