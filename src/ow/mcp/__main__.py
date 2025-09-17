from mcp.server.fastmcp import FastMCP

from ow.workspace.mcp import (
    register_workspace_initialize,
    register_workspace_resources,
    register_workspace_tools,
)

app = FastMCP(name="out-workspace")

_ = register_workspace_initialize(app)
_ = register_workspace_resources(app)
_ = register_workspace_tools(app)


def main():
    """Entry point for the direct execution server."""
    app.run()


if __name__ == "__main__":
    main()
