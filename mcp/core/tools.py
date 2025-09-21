import inspect
import base64
import os
from pydantic import BaseModel
from typing import Optional, Union, BinaryIO

from pydantic import BaseModel

from .rpc import JsonSchema, JsonSchemaTypes
from .primitives import FeatureSchemaAssembler, FeatureContainer


class ToolsDefinitionSchema(BaseModel):
    name: str
    title: Optional[str] = None
    description: Optional[str] = None
    input_schema: Optional[JsonSchema] = None
    output_schema: Optional[JsonSchema] = None
    annotations: Optional[dict] = None


# result schema
class ListResultSchema(BaseModel):
    tools: list[ToolsDefinitionSchema]


class CallResultSchema(BaseModel):
    content: list[dict]
    structuredContent: dict


# Tools function return classes
class UnstructuredResultSchema(BaseModel):
    pass


class TextResult(UnstructuredResultSchema):
    type: str = "text"
    text: str


class ImageResult(UnstructuredResultSchema):
    type: str = "image"
    data: str
    mimeType: str

    class MimeTypes:
        PNG = "image/png"
        JPEG = "image/jpeg"
        JPG = "image/jpeg"  # Alias for JPEG
        GIF = "image/gif"
        WEBP = "image/webp"
        BMP = "image/bmp"
        SVG = "image/svg+xml"
        TIFF = "image/tiff"

        @classmethod
        def from_file_name(cls, file_name: str) -> str:
            if not file_name:
                return cls.PNG

            _, ext = os.path.splitext(file_name)
            ext = ext.lower()

            mime_type_map = {
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

            return mime_type_map.get(ext, cls.PNG)

    def __init__(
        self,
        data: str = None,
        mimeType: str = None,
        file: Union[str, BinaryIO] = None,
        **kwargs,
    ):
        if file is not None:
            # Check if file is a string (file path) or file object
            if isinstance(file, str):
                # File path - read the file and convert to base64
                with open(file, "rb") as f:
                    file_content = f.read()
                file_name = file
            else:
                # File object - read directly and convert to base64
                file_content = file.read()
                file_name = getattr(file, "name", None)

            # Convert to base64
            data = base64.b64encode(file_content).decode("utf-8")

            # Detect MIME type from file name/extension using the new method
            mimeType = ImageResult.MimeTypes.from_file_name(file_name)

        super().__init__(data=data, mimeType=mimeType, **kwargs)


class AudioResult(UnstructuredResultSchema):
    type: str = "audio"
    data: str
    mimeType: str

    class MimeTypes:
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
        def from_file_name(cls, file_name: str) -> str:
            if not file_name:
                return cls.WAV

            _, ext = os.path.splitext(file_name)
            ext = ext.lower()

            mime_type_map = {
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

            return mime_type_map.get(ext, cls.WAV)

    def __init__(
        self,
        data: str = None,
        mimeType: str = None,
        file: Union[str, BinaryIO] = None,
        **kwargs,
    ):
        if file is not None:
            # Check if file is a string (file path) or file object
            if isinstance(file, str):
                # File path - read the file and convert to base64
                with open(file, "rb") as f:
                    file_content = f.read()
                file_name = file
            else:
                # File object - read directly and convert to base64
                file_content = file.read()
                file_name = getattr(file, "name", None)

            # Convert to base64
            data = base64.b64encode(file_content).decode("utf-8")

            # Detect MIME type from file name/extension using the new method
            mimeType = AudioResult.MimeTypes.from_file_name(file_name)

        super().__init__(data=data, mimeType=mimeType, **kwargs)


class EmbeddedResourceResult(UnstructuredResultSchema):
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


class ToolsSchemaAssembler(FeatureSchemaAssembler):
    class UnsupportedResultTypeError(FeatureSchemaAssembler.SchemaAssemblerError):
        pass

    def __init__(self):
        self.definition_list = []
        self.unstructured_result_list = []
        self.structured_content_dict = {}

    def add_function_definition(self, func, **extra):
        """Add function definition to schema.
        annotations can be supplied in extra
        """
        definition = ToolsDefinitionSchema()
        definition.name = func.__name__
        definition.description = func.__doc__ or ""

        # add input schema from function parameters
        for param_name, param in inspect.signature(func).parameters.items():
            if param_name == "self":
                continue
            required = param.default == inspect.Parameter.empty
            param_type = JsonSchemaTypes.from_python_type(param.annotation)

            if definition.input_schema is None:
                definition.input_schema = JsonSchema()
            definition.input_schema.add_property(param_name, param_type, required)

        # TODO: add output schema from function return value

        # update definition with extra
        definition = definition.model_copy(update=extra)

        # add definition to definition list
        self.definition_list.append(definition)

        return definition

    def build_list_result_schema(self):
        return ListResultSchema(tools=self.definition_list).model_dump()

    def add_call_result(self, result):
        if not isinstance(result, BaseModel):
            raise self.UnsupportedResultTypeError(
                f"Unsupported result type: {type(result)}"
            )

        if isinstance(result, UnstructuredResultSchema):
            self.unstructured_result_list.append(result.model_dump())
        else:
            self.structured_content_dict.update(result.model_dump())

    def build_call_result_schema(self):
        cal_result_schema = CallResultSchema(
            content=self.unstructured_result_list,
            structuredContent=self.structured_content_dict,
        ).model_dump()

        # clean up
        self.unstructured_result_list = []
        self.structured_content_dict = {}

        return cal_result_schema


ToolsContainer = FeatureContainer(ToolsSchemaAssembler())
