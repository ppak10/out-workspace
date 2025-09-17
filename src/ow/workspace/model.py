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
            path = self.workspace_path / "workspace.json"

        path.parent.mkdir(parents=True, exist_ok=True)
        _ = path.write_text(self.model_dump_json(indent=2))

        return path

    @classmethod
    def load(cls: type["Workspace"], path: Path) -> "Workspace":
        if not path.exists():
            raise FileNotFoundError(f"Config file not found at {path}")

        return cls.model_validate_json(path.read_text())
