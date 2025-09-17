from mcp.server import FastMCP


def register_workspace_tools(app: FastMCP):
    from ow.mcp.types import ToolSuccess
    from ow.mcp.utils import tool_success
    from ow.workspace.model import Workspace

    @app.tool(
        title="List Workspaces",
        description="Provides a list of created workspaces.",
        structured_output=True,
    )
    def workspaces() -> ToolSuccess[list[str] | None]:
        from ow.workspace.tools.list import list_workspaces

        return tool_success(list_workspaces())

    @app.tool(
        title="List Workspace Subfolders",
        description="Lists of registered subfolders in a given workspace.",
        structured_output=True,
    )
    def workspace_subfolders(workspace_name: str) -> ToolSuccess[list[str] | None]:
        from ow.workspace.tools.list import list_workspace_subfolders

        return tool_success(list_workspace_subfolders(workspace_name))

    @app.tool(
        title="List Workspace Subfolder Content",
        description="Lists content within a registered subfolder for a workspace.",
        structured_output=True,
    )
    def workspace_subfolder_content(
        workspace_name: str, subfolder_name: str
    ) -> ToolSuccess[list[str] | None]:
        from ow.workspace.tools.list import list_workspace_subfolder_content

        return tool_success(
            list_workspace_subfolder_content(workspace_name, subfolder_name)
        )

    _ = (workspaces, workspace_subfolders, workspace_subfolder_content)

    @app.tool(
        title="Create Workspace Subfolder",
        description="Creates and registers a subfolder for a specific workspace",
        structured_output=True,
    )
    def workspace_subfolder_create(
        workspace_name: str, subfolder_name: str, force: bool = False
    ) -> ToolSuccess[Workspace | None]:
        from ow.workspace.tools.create import create_workspace_subfolder

        return tool_success(
            create_workspace_subfolder(workspace_name, subfolder_name, force=force)
        )

    _ = (
        workspaces,
        workspace_subfolders,
        workspace_subfolder_content,
        workspace_subfolder_create,
    )
