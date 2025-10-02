"""
JSON-RPC 2.0 Pydantic schemas for validation.
"""

from typing import Any, Union, Optional
from pydantic import BaseModel, Field


class JsonRpcRequest(BaseModel):
    """JSON-RPC 2.0 request object schema."""

    jsonrpc: str = Field(..., regex="^2\\.0$", description="JSON-RPC version")
    method: str = Field(..., description="Method name to invoke")
    params: Optional[dict] = Field({}, description="Method parameters")
    id: Optional[Union[str, int, None]] = Field(None, description="Request identifier")


class JsonRpcError(BaseModel):
    """JSON-RPC 2.0 error object schema."""

    code: int = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    data: Optional[Any] = Field(None, description="Additional error data")


class JsonRpcSuccessResponse(BaseModel):
    """JSON-RPC 2.0 success response object schema."""

    jsonrpc: str = "2.0"
    result: Any = Field(..., description="Method result")
    id: Optional[Union[str, int, None]] = Field(..., description="Request identifier")


class JsonRpcErrorResponse(BaseModel):
    """JSON-RPC 2.0 error response object schema."""

    jsonrpc: str = "2.0"
    error: JsonRpcError = Field(..., description="Error details")
    id: Optional[Union[str, int, None]] = Field(..., description="Request identifier")
