from pydantic import BaseModel
from typing import Optional, Dict, Any, List, Union
from ..base.schema import JsonSchema
from ..resource.schema import TextContentSchema, BinaryContentSchema


class ToolsDefinitionSchema(BaseModel):
    name: str
    title: Optional[str] = None
    description: Optional[str] = None
    inputSchema: Optional[JsonSchema] = None
    outputSchema: Optional[JsonSchema] = None
    annotations: Optional[Dict[str, Any]] = None


class ToolsListSchema(BaseModel):
    tools: List[dict]


# Content schema classes for tools
class TextContent(BaseModel):
    type: str = "text"
    text: str


class ImageContent(BaseModel):
    type: str = "image"
    data: str  # Base64-encoded image data
    mimeType: str
    annotations: Optional[Dict[str, Any]] = None


class AudioContent(BaseModel):
    type: str = "audio"
    data: str  # Base64-encoded audio data
    mimeType: str
    annotations: Optional[Dict[str, Any]] = None


class ResourceLinkContent(BaseModel):
    type: str = "resource_link"
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = None
    annotations: Optional[Dict[str, Any]] = None


class EmbeddedResource(BaseModel):
    type: str = "resource"
    resource: Union[TextContentSchema, BinaryContentSchema]

class ContentSchema(BaseModel):
    content: Optional[list[dict]] = None
    structuredContent: Optional[dict] = None
