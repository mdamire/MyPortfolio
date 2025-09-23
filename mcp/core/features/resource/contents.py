from ..base.contents import (
    ImageContentSanitizer,
    AudioContentSanitizer,
    TextContentSanitizer,
    MimeTypes,
)
from .schema import ContentSchema, AnnotationSchema
import base64


class ResourceData:
    def __init__(
        self,
        uri: str,
        name: str = None,
        title: str = None,
        description: str = None,
        mime_type: str = None,
        size: int = None,
        annotations: dict = None,
    ):
        self.uri = uri
        self.name = name
        self.title = title
        self.description = description
        self.mime_type = mime_type
        self.size = size
        self.annotations = annotations


class TextContent:
    def __init__(
        self,
        text: str,
        uri: str = None,
        name: str = None,
        title: str = None,
        mime_type: str = None,
        annotations: dict = None,
    ):
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")

        self.uri = uri
        self.text = text
        self.name = name
        self.title = title
        self.mime_type = mime_type
        self.annotations = annotations


class BinaryContent:
    def __init__(
        self,
        blob: str,
        uri: str = None,
        name: str = None,
        title: str = None,
        mime_type: str = None,
        annotations: dict = None,
    ):
        if not blob or not isinstance(blob, str):
            raise ValueError("Blob must be a non-empty string")

        # Validate base64 format
        try:
            base64.b64decode(blob, validate=True)
        except Exception:
            raise ValueError("Blob must be valid base64 encoded data")

        self.uri = uri
        self.blob = blob
        self.name = name
        self.title = title
        self.mime_type = mime_type
        self.annotations = annotations


class ResourceContent:
    class FileProcessError(Exception):
        pass

    def __init__(self):
        self.content_list = []

    def add_text_content(
        self,
        text: str,
        uri: str = None,
        name: str = None,
        title: str = None,
        mime_type: str = None,
        annotations: dict = None,
    ):
        text_content = TextContent(
            text=text,
            uri=uri,
            name=name,
            title=title,
            mime_type=mime_type,
            annotations=annotations,
        )
        self.content_list.append(text_content)
        return text_content

    def add_binary_content(
        self,
        blob: str,
        uri: str = None,
        name: str = None,
        title: str = None,
        mime_type: str = None,
        annotations: dict = None,
    ):
        binary_content = BinaryContent(
            blob=blob,
            uri=uri,
            name=name,
            title=title,
            mime_type=mime_type,
            annotations=annotations,
        )
        self.content_list.append(binary_content)
        return binary_content

    def add_file(
        self,
        file: str,
        uri: str = None,
        name: str = None,
        title: str = None,
        mime_type: str = None,
        annotations: dict = None,
    ):
        # Check text content
        sanitized_content = TextContentSanitizer(file=file)
        if sanitized_content.text and sanitized_content.mime_type:
            return self.add_text_content(
                text=sanitized_content.text,
                uri=uri,
                name=name,
                title=title,
                mime_type=mime_type or sanitized_content.mime_type,
                annotations=annotations,
            )

        for binary_sanitizer in [ImageContentSanitizer, AudioContentSanitizer]:
            # Check binary content
            sanitized_content = binary_sanitizer(file=file)
            if sanitized_content.data and sanitized_content.mime_type:
                return self.add_binary_content(
                    blob=sanitized_content.data,
                    uri=uri,
                    name=name,
                    title=title,
                    mime_type=mime_type or sanitized_content.mime_type,
                    annotations=annotations,
                )

        raise self.FileProcessError(f"Failed to process for file: {file}")
