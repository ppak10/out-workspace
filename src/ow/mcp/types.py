from typing import Any, TypeVar, Generic
from pydantic import BaseModel

# Generic type for the success data
T = TypeVar("T")


class ToolError(BaseModel):
    """Standard error response for MCP tools."""

    success: bool = False
    error: str
    error_code: str
    details: dict[str, Any] = {}


class ToolSuccess(BaseModel, Generic[T]):
    """Standard success response for MCP tools."""

    success: bool = True
    data: T


# Type alias for tool responses
ToolResponse = ToolSuccess[T] | ToolError
