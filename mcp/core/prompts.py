from pydantic import BaseModel, field_validator
from typing import Optional, List
import inspect
import re
import logging
from datetime import datetime
from enum import Enum

from .primitives import FeatureSchemaAssembler, FeatureContainer
from .rpc import RPCResponseSchema
from .contents import BinaryContent, ImageContent, AudioContent


# Schema classes following the same pattern as tools
class PromptArgumentDefinition(BaseModel):
    name: str
    description: Optional[str] = None
    required: bool = False


class PromptsDefinitionSchema(BaseModel):
    name: str
    title: Optional[str] = None
    description: Optional[str] = None
    arguments: Optional[List[PromptArgumentDefinition]] = None


class ListResultSchema(BaseModel):
    prompts: List[PromptsDefinitionSchema]


class CallResultSchema(BaseModel):
    description: str
    messages: List[dict]


class PromptsSchemaAssembler(FeatureSchemaAssembler):
    class UnsupportedResultTypeError(FeatureSchemaAssembler.SchemaAssemblerError):
        pass

    def __init__(self):
        self.definition_list = []
        self.message_list = []
        self.description = ""

    def _parse_docstring_structure(self, docstring):
        """Parse docstring into title, description, and parameters.

        Returns:
            dict with keys: 'title', 'description', 'params'
        """
        if not docstring:
            return {"title": None, "description": "", "params": {}}

        # Split docstring into lines and clean up
        lines = docstring.strip().split("\n")
        lines = [line.rstrip() for line in lines]

        title = None
        description_lines = []
        params = {}

        # Check if first line is title (followed by empty line or end)
        if len(lines) > 1 and lines[1].strip() == "":
            title = lines[0].strip()
            start_idx = 2  # Skip title and empty line
        elif len(lines) == 1:
            title = lines[0].strip()
            start_idx = 1
        else:
            start_idx = 0

        # Find where parameters section starts
        param_start_idx = len(lines)
        param_keywords = ["Args:", "Arguments:", "Parameters:", "Param:"]

        for i in range(start_idx, len(lines)):
            line = lines[i].strip()
            if any(line.startswith(keyword) for keyword in param_keywords):
                param_start_idx = i
                break
            # Check for Sphinx style parameters
            if line.startswith(":param"):
                param_start_idx = i
                break
            # Check for NumPy style parameters
            if (
                line == "Parameters"
                and i + 1 < len(lines)
                and re.match(r"^-+$", lines[i + 1].strip())
            ):
                param_start_idx = i
                break

        # Extract description (everything between title and parameters)
        for i in range(start_idx, param_start_idx):
            line = lines[i].strip()
            if line:  # Skip empty lines within description
                description_lines.append(line)

        description = " ".join(description_lines)

        # Extract parameters from the parameters section
        if param_start_idx < len(lines):
            param_section = "\n".join(lines[param_start_idx:])
            params = self._parse_docstring_params(param_section)

        return {"title": title, "description": description, "params": params}

    def _parse_docstring_params(self, docstring):
        """Parse parameter descriptions from docstring.
        Supports Google, NumPy, and Sphinx style docstrings.
        """
        if not docstring:
            return {}

        param_descriptions = {}

        # Google style: Args: or Parameters:
        google_match = re.search(
            r"(?:Args?|Arguments?|Parameters?):\s*\n(.*?)(?:\n\n|\n[A-Z]|\Z)",
            docstring,
            re.DOTALL | re.IGNORECASE,
        )
        if google_match:
            params_section = google_match.group(1)
            # Match param_name: description or param_name (type): description
            for match in re.finditer(
                r"^\s*(\w+)(?:\s*\([^)]+\))?\s*:\s*(.+?)(?=^\s*\w+\s*(?:\([^)]+\))?\s*:|$)",
                params_section,
                re.MULTILINE | re.DOTALL,
            ):
                param_name = match.group(1).strip()
                description = re.sub(r"\s+", " ", match.group(2).strip())
                param_descriptions[param_name] = description

        # NumPy style: Parameters followed by dashes
        numpy_match = re.search(
            r"Parameters\s*\n\s*-+\s*\n(.*?)(?:\n\s*\n|\n[A-Z]|\Z)",
            docstring,
            re.DOTALL | re.IGNORECASE,
        )
        if numpy_match:
            params_section = numpy_match.group(1)
            # Match param_name : type and description on next lines
            for match in re.finditer(
                r"^(\w+)\s*:.*?\n(.*?)(?=^\w+\s*:|$)",
                params_section,
                re.MULTILINE | re.DOTALL,
            ):
                param_name = match.group(1).strip()
                description = re.sub(r"\s+", " ", match.group(2).strip())
                param_descriptions[param_name] = description

        # Sphinx style: :param param_name: description
        sphinx_matches = re.findall(
            r":param\s+(\w+)\s*:\s*(.+?)(?=\n\s*:|\n\s*\n|\Z)", docstring, re.DOTALL
        )
        for param_name, description in sphinx_matches:
            param_descriptions[param_name.strip()] = re.sub(
                r"\s+", " ", description.strip()
            )

        return param_descriptions

    def add_function_definition(self, func, **extra):
        """Add function (prompt) definition to schema.
        annotations can be supplied in extra
        """
        definition = PromptsDefinitionSchema()
        definition.name = func.__name__

        # Parse docstring structure
        docstring_info = self._parse_docstring_structure(func.__doc__)

        # Set title and description
        if docstring_info["title"]:
            definition.title = docstring_info["title"]

        if docstring_info["description"]:
            definition.description = docstring_info["description"]

        # add input schema from function parameters
        arguments = []
        for param_name, param in inspect.signature(func).parameters.items():
            if param_name == "self":
                continue
            required = param.default == inspect.Parameter.empty
            description = docstring_info["params"].get(param_name, None)
            arguments.append(
                PromptArgumentDefinition(
                    name=param_name, description=description, required=required
                )
            )

        definition.arguments = arguments if arguments else None

        # update definition with extra
        definition = definition.model_copy(update=extra)

        # add definition to definition list
        self.definition_list.append(definition)

        return definition

    def build_list_result_schema(self):
        return ListResultSchema(prompts=self.definition_list).model_dump()

    def add_call_result(self, result):
        # TODO
        if not isinstance(result, BaseModel):
            raise self.UnsupportedResultTypeError(
                f"Unsupported result type: {type(result)}"
            )

        result_dict = result.model_dump()
        if "description" in result_dict:
            self.description = result_dict["description"]
        if "messages" in result_dict:
            self.message_list.extend(result_dict["messages"])

    def build_call_result_schema(self):
        call_result_schema = CallResultSchema(
            description=self.description, messages=self.message_list
        ).model_dump()

        # clean up
        self.message_list = []
        self.description = ""

        return call_result_schema


PromptsContainer = FeatureContainer(PromptsSchemaAssembler())


# ---
class PromptArgumentDefinition:
    def __init__(self):
        self.argument_definition_list = []

    def add_argument_definition(self, name, description=None, required=False):
        schema = {"name": name, "required": required}
        if description:
            schema["description"] = description
        self.argument_definition_list.append(schema)
        return schema

    def build_schema(self):
        return self.argument_definition_list


class PromptSchema:
    class PromptRole(Enum):
        USER = "user"
        ASSISTANT = "assistant"

    def __init__(self):
        self.definition_list = []
        self.message_list = []
        self.list_schema = None

    def add_prompt_definition(
        self,
        name,
        title=None,
        description=None,
        arguments: PromptArgumentDefinition = None,
    ):
        schema = {
            "name": name,
        }
        if title:
            schema["title"] = title
        if description:
            schema["description"] = description
        if arguments:
            schema["arguments"] = arguments.build_schema()
        self.definition_list.append(schema)
        return schema

    def add_text_message(self, role: PromptRole, text):
        schema = {"role": role, "content": {"type": "text", "text": text}}
        self.message_list.append(schema)
        return schema

    def add_image_message(self, role: PromptRole, data):
        schema = {
            "role": role,
            "content": {"type": "image", "data": data, "mimeType": "image/png"},
        }
        self.message_list.append(schema)
        return schema

    def add_audio_message(self, role: PromptRole, data):
        schema = {
            "role": role,
            "content": {"type": "audio", "data": data, "mimeType": "audio/wav"},
        }
        self.message_list.append(schema)
        return schema

    def add_embedded_resource_message(
        self, role: PromptRole, uri, name, title, mime_type, text
    ):
        schema = {
            "type": "resource",
            "resource": {
                "uri": uri,
                "name": name,
                "title": title,
                "mimeType": mime_type,
                "text": text,
            },
        }
        self.message_list.append(schema)
        return schema

    def build_list_schema(self, id):
        rpc_response_schema = RPCResponseSchema(id)
        schema = {"prompts": self.message_list}
        self.list_schema = rpc_response_schema.build_success_schema(schema)
        return self.list_schema

    def build_message_schema(self, id, description):
        rpc_response_schema = RPCResponseSchema(id)
        schema = {"description": description, "messages": self.message_list}
        self.schema = rpc_response_schema.build_success_schema(schema)
        return self.schema


class AnnotationSchema(BaseModel):
    class AudienceType(Enum):
        USER = "user"
        ASSISTANT = "assistant"

    audience: Optional[str] = None
    priority: Optional[float] = None
    lastModified: Optional[str] = None

    @field_validator("audience")
    @classmethod
    def validate_audience(cls, v):
        if v is not None:
            valid_values = [e.value for e in cls.AudienceType]
            if v not in valid_values:
                logging.error(
                    f"Invalid audience value '{v}'. Must be one of: {valid_values}"
                )
                return None
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v):
        if v is not None:
            if not isinstance(v, (int, float)) or not (0.0 <= v <= 1.0):
                logging.error(
                    f"Invalid priority value '{v}'. Must be a float between 0.0 and 1.0"
                )
                return None
        return v

    @field_validator("lastModified")
    @classmethod
    def validate_last_modified(cls, v):
        if v is not None:
            if isinstance(v, datetime):
                return v.isoformat()

            if isinstance(v, str):
                try:
                    datetime.fromisoformat(v.replace("Z", "+00:00"))
                    return v
                except ValueError:
                    logging.error(
                        f"Invalid ISO 8601 timestamp '{v}'. Using current timestamp."
                    )
                    return None
        return v


class ResourceContent:
    class Schema(BaseModel):
        uri: str = None
        name: str = None
        title: str = None
        mimeType: str = None
        text: str = None
        blob: str = None
        annotations: Optional[AnnotationSchema] = None

    def __init__(self):
        self.content_list = []

    def add_function_details(self):
        pass

    def add_text_content(self, text, mime_type, annotations: AnnotationSchema = None):
        schema = self.Schema(text=text, mimeType=mime_type)
        if annotations:
            schema.annotations = annotations
        self.content_list.append(schema)
        return schema

    def add_binary_content(
        self, blob=None, mime_type=None, file=None, annotations: AnnotationSchema = None
    ):
        for content_class in [ImageContent, AudioContent]:
            content = content_class(data=blob, mimeType=mime_type, file=file)
            if content.data and content.mimeType:
                break

        # Create schema with the processed content
        schema = self.Schema(blob=content.data, mimeType=content.mimeType)
        if annotations:
            schema.annotations = annotations
        self.content_list.append(schema)
        return schema
