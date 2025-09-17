from mcp.server import FastMCP


def register_workspace_resources(app: FastMCP):

    @app.resource("workspace://")
    def workspaces() -> list[str] | None:
        from ow.workspace.tools.list import list_workspaces

        return list_workspaces()

    @app.resource("workspace://{workspace}/")
    def workspace_subfolders(workspace: str) -> list[str] | None:
        from ow.workspace.tools.list import list_workspace_subfolders

        return list_workspace_subfolders(workspace)

    @app.resource("workspace://{workspace}/{subfolder}/")
    def workspace_subfolder_content(workspace: str, subfolder: str) -> list[str] | None:
        from ow.workspace.tools.list import list_workspace_subfolder_content

        return list_workspace_subfolder_content(workspace, subfolder)

    _ = (workspaces, workspace_subfolders, workspace_subfolder_content)
