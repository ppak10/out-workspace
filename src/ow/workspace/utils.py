import importlib.util

from pathlib import Path


def get_project_root(parents_index: int = 4) -> Path:
    """Find project root based on package installation location."""
    try:
        spec = importlib.util.find_spec("ow")
        if spec and spec.origin:
            package_path = Path(spec.origin).parent
            parent_folder = package_path.parent.name
            if parent_folder == "src":
                # Local Development
                # package_path: /.../out-workspace/src/ow
                # package_path.parent.parent: /.../out-workspace
                return package_path.parent.parent
            else:
                # PyPI Install
                # package_path: /.../out-workspace-agent/.venv/lib/python3.13/site-packages/ow
                # package_path.parents[parents_index]: /.../out-workspace-agent
                return package_path.parents[parents_index]
    except ImportError:
        pass
    return Path.cwd()
