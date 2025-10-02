from ..base.contents import (
    TextContentSanitizer,
    ImageContentSanitizer,
    AudioContentSanitizer,
)
from .schema import (
    TextContent,
    ImageContent,
    AudioContent,
    EmbeddedResource,
    PromptMessageSchema,
)
from ..resource.schema import TextContentSchema, BinaryContentSchema
from typing import Optional, Dict, Any, List, Union
import base64


class PromptsContent:
    class ResourceNotFoundError(Exception):
        pass

    class ResourceContainerRequiredError(Exception):
        pass

    def __init__(
        self,
        role: Optional[str] = None,
        resource_container=None,
        description: Optional[str] = None,
    ):
        self.messages = []
        self.default_role = role
        self.resource_container = resource_container
        self.description = description

    def _add_message(self, role: str, content: Union[str, List[Dict[str, Any]]]):
        """Add a message with role and content."""
        if not role:
            raise ValueError("Role is required for message")
        if not content:
            raise ValueError("Content is required for message")

        message = PromptMessageSchema(role=role, content=content)
        self.messages.append(message)
        return message

    def add_text(
        self,
        text: str,
        role: Optional[str] = None,
        annotations: Optional[Dict[str, Any]] = None,
    ):
        """Add text content as a message."""
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")

        text_content = TextContent(text=text, annotations=annotations)
        self._add_message(role or self.default_role, text_content)

        return text_content

    def add_image(
        self,
        data: str,
        mime_type: str,
        role: Optional[str] = None,
        annotations: Optional[Dict[str, Any]] = None,
    ):
        """Add image content as a message."""
        if not data or not isinstance(data, str):
            raise ValueError("Data must be a non-empty string")
        if not mime_type:
            raise ValueError("MIME type is required for image content")

        try:
            base64.b64decode(data, validate=True)
        except Exception:
            raise ValueError("Data must be valid base64 encoded string")

        image_content = ImageContent(
            data=data, mimeType=mime_type, annotations=annotations
        )
        self._add_message(role or self.default_role, image_content)
        return image_content

    def add_audio(
        self,
        data: str,
        mime_type: str,
        role: Optional[str] = None,
        annotations: Optional[Dict[str, Any]] = None,
    ):
        """Add audio content as a message."""
        if not data or not isinstance(data, str):
            raise ValueError("Data must be a non-empty string")
        if not mime_type:
            raise ValueError("MIME type is required for audio content")

        try:
            base64.b64decode(data, validate=True)
        except Exception:
            raise ValueError("Data must be valid base64 encoded string")

        audio_content = AudioContent(
            data=data, mimeType=mime_type, annotations=annotations
        )
        self._add_message(role or self.default_role, audio_content)
        return audio_content

    def add_file(
        self,
        file: str,
        role: Optional[str] = None,
        annotations: Optional[Dict[str, Any]] = None,
    ):
        """Add content from file as a message - automatically detects if it's text, image, or audio."""
        try:
            text_sanitizer = TextContentSanitizer(file=file)
            if text_sanitizer.text and text_sanitizer.mime_type:
                return self.add_text(text_sanitizer.text, role, annotations)
        except Exception:
            pass

        try:
            image_sanitizer = ImageContentSanitizer(file=file)
            if image_sanitizer.data and image_sanitizer.mime_type:
                return self.add_image(
                    image_sanitizer.data, image_sanitizer.mime_type, role, annotations
                )
        except Exception:
            pass

        try:
            audio_sanitizer = AudioContentSanitizer(file=file)
            if audio_sanitizer.data and audio_sanitizer.mime_type:
                return self.add_audio(
                    audio_sanitizer.data, audio_sanitizer.mime_type, role, annotations
                )
        except Exception:
            pass

        raise ValueError(f"Unable to process file: {file}")

    def add_embedded_resource(
        self,
        uri: str,
        role: Optional[str] = None,
        name: Optional[str] = None,
        title: Optional[str] = None,
        mime_type: Optional[str] = None,
        text: Optional[str] = None,
        blob: Optional[str] = None,
        annotations: Optional[Dict[str, Any]] = None,
    ):
        """Add embedded resource content as a message."""

        resource_content = {}
        if self.resource_container:
            try:
                resource_result = self.resource_container.call(uri)
                resource_content = resource_result["contents"][0]
            except Exception:
                if not text and not blob:
                    raise self.ResourceNotFoundError(
                        f"Resource with URI '{uri}' not found in ResourceContainer"
                    )
        else:
            if not text and not blob:
                raise self.ResourceContainerRequiredError(
                    "ResourceContainer is required when only URI is provided for embedded resource"
                )

        text = text or resource_content.get("text")
        blob = blob or resource_content.get("blob")
        mime_type = mime_type or resource_content.get("mimeType")

        if not mime_type:
            raise ValueError("MIME type is required for embedded resource")

        content_data = {
            "uri": uri,
            "mimeType": mime_type,
            "name": name or resource_content.get("name"),
            "title": title or resource_content.get("title"),
            "annotations": annotations or resource_content.get("annotations"),
        }

        if text:
            resource_schema = TextContentSchema(
                text=text,
                **content_data,
            )
        elif blob:
            resource_schema = BinaryContentSchema(
                blob=blob,
                **content_data,
            )
        else:
            raise ValueError(
                "Either 'text' or 'blob' must be provided for embedded resource"
            )

        embedded_resource = EmbeddedResource(resource=resource_schema)
        self._add_message(role or self.default_role, embedded_resource.model_dump())
        return embedded_resource
