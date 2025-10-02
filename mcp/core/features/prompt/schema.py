from pydantic import BaseModel
from typing import Optional, Dict, Any, List, Union
from ..resource.schema import TextContentSchema, BinaryContentSchema


class PromptDefinitionSchema(BaseModel):
    name: str
    title: Optional[str] = None
    description: Optional[str] = None
    arguments: Optional[List[Dict[str, Any]]] = None


class PromptsListSchema(BaseModel):
    prompts: List[dict]
    nextCursor: Optional[str] = None


# 'Getting a prompt' schema classes
class TextContent(BaseModel):
    type: str = "text"
    text: str
    annotations: Optional[Dict[str, Any]] = None


class ImageContent(BaseModel):
    type: str = "image"
    data: str
    mimeType: str
    annotations: Optional[Dict[str, Any]] = None


class AudioContent(BaseModel):
    type: str = "audio"
    data: str
    mimeType: str
    annotations: Optional[Dict[str, Any]] = None


class EmbeddedResource(BaseModel):
    type: str = "resource"
    resource: Union[TextContentSchema, BinaryContentSchema]


class PromptMessageSchema(BaseModel):
    role: str
    content: dict


class PromptResultSchema(BaseModel):
    description: Optional[str] = None
    messages: List[dict]
