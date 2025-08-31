import json
from enum import Enum


class SchemaTypes(Enum):
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    NULL = "null"


class RPCResponseSchema:
    def __init__(self, id):
        self.id = id
        self.schema = {
            "jsonrpc": "2.0",
            "id": self.id,
        }

    def build_success_schema(self, result):
        self.schema["result"] = result
        return self.schema

    def build_error_schema(self, code, message, data=None):
        error = {"code": code, "message": message}
        if data:
            error["data"] = data
        self.schema["error"] = error
        return self.schema


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


class ResourceSchema:
    def __init__(self):
        self.resource_definition_list = []
        self.template_definition_list = []
        self.resource_content_list = []
        self.reading_schema = None
        self.listing_schema = None

    class UriType(Enum):
        HTTP = "http://"
        HTTPS = "https://"
        FILE = "file://"
        GIT = "git://"

    def make_uri(self, uri_type: UriType, uri):
        return f"{uri_type}{uri}"

    def add_resource_definition(
        self,
        uri,
        name,
        title=None,
        description=None,
        mime_type=None,
        size=None,
        annotations: dict = None,
    ):
        schema = {"uri": uri, "name": name}
        if title:
            schema["title"] = title
        if description:
            schema["description"] = description
        if mime_type:
            schema["mimeType"] = mime_type
        if size:
            schema["size"] = size
        if annotations:
            schema["annotations"] = annotations
        self.resource_definition_list.append(schema)
        return schema

    def add_resource_template(
        self,
        uri_template,
        name,
        title=None,
        description=None,
        mime_type=None,
        annotations: dict = None,
    ):
        schema = {"uriTemplate": uri_template, "name": name}
        if title:
            schema["title"] = title
        if description:
            schema["description"] = description
        if mime_type:
            schema["mimeType"] = mime_type
        if annotations:
            schema["annotations"] = annotations
        self.template_definition_list.append(schema)
        return schema

    def add_text_content(
        self, uri, text, name=None, title=None, mime_type=None, annotations: dict = None
    ):
        schema = {"uri": uri, "text": text}
        if name:
            schema["name"] = name
        if title:
            schema["title"] = title
        if mime_type:
            schema["mimeType"] = mime_type
        if annotations:
            schema["annotations"] = annotations
        self.resource_content_list.append(schema)
        return schema

    def add_binary_content(
        self, uri, data, name=None, title=None, mime_type=None, annotations: dict = None
    ):
        schema = {"uri": uri, "blob": data}
        if name:
            schema["name"] = name
        if title:
            schema["title"] = title
        if mime_type:
            schema["mimeType"] = mime_type
        if annotations:
            schema["annotations"] = annotations
        self.resource_content_list.append(schema)
        return schema

    def build_reading_schema(self, id):
        rpc_response_schema = RPCResponseSchema(id)
        schema = {"contents": self.resource_content_list}
        self.reading_schema = rpc_response_schema.build_success_schema(schema)
        return self.reading_schema

    def build_listing_schema(self, id):
        rpc_response_schema = RPCResponseSchema(id)
        schema = {
            "resources": self.resource_definition_list,
            "resourceTemplates": self.template_definition_list,
        }
        self.listing_schema = rpc_response_schema.build_success_schema(schema)
        return self.listing_schema

    def build_resouce_not_found_error(self, id, uri):
        rpc_response_schema = RPCResponseSchema(id)
        schema = rpc_response_schema.build_error_schema(
            code=-32002, message="Resource not found", data={"uri": uri}
        )
        return schema


class ToolInputDefinitionSchema:
    def __init__(self):
        self.schema = {"type": "object", "properties": {}, "required": []}

    def add_property(
        self, name, prop_type: SchemaTypes, description=None, required=False
    ):
        property_def = {"type": prop_type}
        if description:
            property_def["description"] = description

        self.schema["properties"][name] = property_def

        if required:
            self.schema["required"].append(name)

        return self

    def build_schema(self):
        return self.schema


class ToolOutputDefinitionSchema:
    def __init__(self):
        self.schema = {"type": "object", "properties": {}, "required": []}

    def add_property(
        self, name, prop_type: SchemaTypes, description=None, required=False
    ):
        property_def = {"type": prop_type}
        if description:
            property_def["description"] = description

        self.schema["properties"][name] = property_def

        if required:
            self.schema["required"].append(name)

        return self

    def build_schema(self):
        return self.schema


class ToolsSchema:
    def __init__(self):
        self.definition_schema_list = []
        self.output_non_structured_schema_list = []
        self.output_structured_content = {}
        self.listing_schema = None
        self.output_schema = None

    def add_definition(
        self,
        name,
        title=None,
        description=None,
        input_schema: ToolInputDefinitionSchema = None,
        output_schema: ToolOutputDefinitionSchema = None,
        annotations: dict = None,
    ):
        schema = {}
        schema["name"] = name
        if title:
            schema["title"] = title
        if description:
            schema["description"] = description
        if input_schema:
            schema["inputSchema"] = input_schema.build_schema()
        if output_schema:
            schema["outputSchema"] = output_schema.build_schema()
        if annotations:
            schema["annotations"] = annotations
        self.definition_schema_list.append(schema)
        return schema

    def add_text_output(self, text):
        schema = {"type": "text", "text": text}
        self.output_non_structured_schema_list.append(schema)
        return schema

    def add_image_output(self, data):
        schema = {"type": "image", "data": data, "mimeType": "image/png"}
        self.output_non_structured_schema_list.append(schema)
        return schema

    def add_audio_output(self, data):
        schema = {"type": "audio", "data": data, "mimeType": "audio/wav"}
        self.output_non_structured_schema_list.append(schema)
        return schema

    def add_embedded_resource(self, uri, name, title, mime_type, text):
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
        self.output_non_structured_schema_list.append(schema)
        return schema

    def add_structured_content(self, content: dict = {}, **kwargs):
        self.output_structured_content.update(content)
        self.output_structured_content.update(kwargs)
        return self.output_structured_content

    def build_listing_schema(self, id):
        rpc_response_schema = RPCResponseSchema(id)
        schema = {"tools": self.definition_schema_list}
        self.listing_schema = rpc_response_schema.build_success_schema(schema)
        return self.listing_schema

    def build_output_schema(self, id, is_error=False):
        rpc_response_schema = RPCResponseSchema(id)
        schema = {}
        if self.output_non_structured_schema_list:
            schema["content"] = self.output_non_structured_schema_list
        if self.output_structured_content:
            schema["structuredContent"] = self.output_structured_content
        schema["isError"] = is_error
        self.output_schema = rpc_response_schema.build_success_schema(schema)
        return self.output_schema

    def build_unknown_tool_error_schema(self, id, tool_name):
        rpc_response_schema = RPCResponseSchema(id)
        schema = rpc_response_schema.build_error_schema(
            code=-32602,
            message=f"Unknown tool: {tool_name}",
        )
        return schema
