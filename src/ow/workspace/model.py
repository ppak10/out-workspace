import re

from pathlib import Path
from pydantic import BaseModel, field_validator, model_validator

from .utils import get_project_root


class Workspace(BaseModel):
    """
    Metadata for workspace.
    """

    name: str
    out_path: Path | None = None
    workspace_path: Path | None = None
    subfolders: list[str] = []
    config_file: str = "workspace.json"

    @field_validator("name", mode="before")
    @classmethod
    def normalize_and_sanitize_name(cls, v: str) -> str:
        v = v.replace(" ", "_")
        v = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "", v)
        return v[:255]

    @model_validator(mode="after")
    def populate_missing_paths(self) -> "Workspace":
        if not self.out_path:
            self.out_path = get_project_root() / "out"

        if not self.workspace_path:
            self.workspace_path = self.out_path / self.name

        return self

    def create_subfolders(self) -> list[Path]:
        """
        Create subfolders defined in self.subfolders under workspace_path.
        Returns a list of created Path objects.
        """
        if not self.workspace_path:
            raise ValueError("workspace_path must be set before creating subfolders.")

        created = []
        for folder in self.subfolders:
            folder_path = self.workspace_path / folder
            folder_path.mkdir(parents=True, exist_ok=True)
            created.append(folder_path)

        self.save()
        return created

    def add_subfolder(self, subfolder_name: str) -> Path:
        """
        Add and create a new subfolder inside the workspace.

        Args:
            subfolder_name (str): Name of the subfolder to create.

        Returns:
            Path: The path of the created subfolder.

        Raises:
            ValueError: If the subfolder name contains path separators (nested paths not allowed).
        """
        if not self.workspace_path:
            raise ValueError("workspace_path must be set before adding subfolders.")

        # Check for nested paths (path separators)
        if "/" in subfolder_name or "\\" in subfolder_name:
            raise ValueError(
                "Nested subfolder paths are not allowed. Use simple folder names only."
            )

        safe_name = self.normalize_and_sanitize_name(subfolder_name)
        folder_path = self.workspace_path / safe_name
        folder_path.mkdir(parents=True, exist_ok=True)

        if safe_name not in self.subfolders:
            self.subfolders.append(safe_name)

        self.save()
        return folder_path

    def save(self, path: Path | None = None) -> Path:
        """
        Save the configuration to a YAML file.
        If no path is given, saves to '<workspace_path>/workspace.json'.
        """
        if path is None:
            if not self.workspace_path:
                raise ValueError(
                    "workspace_path must be set to determine save location."
                )
            path = self.workspace_path / self.config_file

        path.parent.mkdir(parents=True, exist_ok=True)
        _ = path.write_text(self.model_dump_json(indent=2))

        return path

    @classmethod
    def load(cls: type["Workspace"], path: Path) -> "Workspace":
        if not path.exists():
            raise FileNotFoundError(f"Workspace file not found at {path}")

        return cls.model_validate_json(path.read_text())
