from .__main__ import app
from .options import WorkspaceOption
from .version import register_version

from ow.mcp.cli import app as mcp_app
from ow.workspace.cli import app as workspace_app

__all__ = ["app", "WorkspaceOption"]

app.add_typer(mcp_app, name="mcp")
app.add_typer(workspace_app, name="workspace")

_ = register_version(app)

if __name__ == "__main__":
    app()
