"""Saved content"""

from pydantic import BaseModel
from typing import Union, BinaryIO
import os
import base64
from enum import Enum
from abc import abstractmethod


class MimeTypeMapper:
    @classmethod
    def _get_file_name_extension(cls, file_name: str) -> str:
        _, ext = os.path.splitext(file_name)
        return ext.lower()

    @abstractmethod
    @classmethod
    def _get_file_extension_mapping(cls) -> dict:
        pass

    @classmethod
    def from_file_name(cls, file_name: str) -> str:
        ext = cls._get_file_name_extension(file_name)
        return cls._get_file_extension_mapping().get(ext, None)


class MimeTypes:
    class Image(Enum, MimeTypeMapper):
        PNG = "image/png"
        JPEG = "image/jpeg"
        JPG = "image/jpeg"  # Alias for JPEG
        GIF = "image/gif"
        WEBP = "image/webp"
        BMP = "image/bmp"
        SVG = "image/svg+xml"
        TIFF = "image/tiff"

        @classmethod
        def _get_file_extension_mapping(cls) -> dict:
            mapping = {
                ".png": cls.PNG,
                ".jpg": cls.JPEG,
                ".jpeg": cls.JPEG,
                ".gif": cls.GIF,
                ".webp": cls.WEBP,
                ".bmp": cls.BMP,
                ".svg": cls.SVG,
                ".tiff": cls.TIFF,
                ".tif": cls.TIFF,
            }
            return mapping

    class Audio(Enum):
        WAV = "audio/wav"
        MP3 = "audio/mpeg"
        AAC = "audio/aac"
        OGG = "audio/ogg"
        FLAC = "audio/flac"
        M4A = "audio/mp4"
        WMA = "audio/x-ms-wma"
        OPUS = "audio/opus"
        WEBM = "audio/webm"

        @classmethod
        def _get_file_extension_mapping(cls) -> dict:
            mapping = {
                ".wav": cls.WAV,
                ".mp3": cls.MP3,
                ".aac": cls.AAC,
                ".ogg": cls.OGG,
                ".oga": cls.OGG,  # Alternative OGG extension
                ".flac": cls.FLAC,
                ".m4a": cls.M4A,
                ".mp4": cls.M4A,  # MP4 audio
                ".wma": cls.WMA,
                ".opus": cls.OPUS,
                ".webm": cls.WEBM,
            }
            return mapping


class BaseContent(BaseModel):
    type: str


class TextContent(BaseContent):
    type: str = "text"
    text: str


class BinaryContent(BaseModel):
    data: str
    mimeType: str
    _mime_type_class = None

    def __init__(
        self,
        data: Union[str, bytes] = None,
        mimeType: str = None,
        file: Union[str, BinaryIO] = None,
        **kwargs,
    ):
        if file is not None:
            if isinstance(file, str):
                with open(file, "rb") as f:
                    file_content = f.read()
                file_name = file
            else:
                file_content = file.read()
                file_name = getattr(file, "name", None)

            # Convert to base64
            data = base64.b64encode(file_content).decode("utf-8")
            mimeType = self._mime_type_class.from_file_name(file_name)

        elif data is None or mimeType is None:
            raise ValueError(
                "Either 'file' must be provided, or both 'data' and 'mimeType' must be provided"
            )

        else:
            if isinstance(data, bytes):
                try:
                    base64.b64decode(data, validate=True)
                    data = data.decode("utf-8")
                except Exception:
                    data = base64.b64encode(data).decode("utf-8")
            elif isinstance(data, str):
                try:
                    base64.b64decode(data, validate=True)
                except Exception:
                    data = base64.b64encode(data.encode("utf-8")).decode("utf-8")

        super().__init__(data=data, mimeType=mimeType, **kwargs)


class ImageContent(BinaryContent):
    type: str = "image"
    _mime_type_class = MimeTypes.Image


class AudioContent(BinaryContent):
    type: str = "audio"
    _mime_type_class = MimeTypes.Audio


class EmbeddedResourceContent(BaseContent):
    uri: str
    name: str
    title: str
    mime_type: str
    text: str

    def model_dump(self):
        return {
            "type": "resource",
            "resource": {
                "uri": self.uri,
                "name": self.name,
                "title": self.title,
                "mimeType": self.mime_type,
                "text": self.text,
            },
        }
