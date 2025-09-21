from enum import Enum
import json
from pydantic import BaseModel
from typing import Optional


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


class JsonSchemaTypes(Enum):
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    NULL = "null"

    class MappingError(Exception):
        pass

    class CastingError(Exception):
        pass

    @classmethod
    def from_python_type(cls, python_type):
        if python_type is str:
            return cls.STRING
        if python_type is int:
            return cls.INTEGER
        if python_type is float:
            return cls.NUMBER
        if python_type is bool:
            return cls.BOOLEAN
        if python_type is list:
            return cls.ARRAY
        if python_type is dict:
            return cls.OBJECT
        if python_type is type(None):
            return cls.NULL
        return cls.STRING

    @classmethod
    def cast_type(cls, value, param_type):
        try:
            if param_type == cls.INTEGER:
                return int(value)
            elif param_type == cls.NUMBER:
                return float(value)
            elif param_type == cls.BOOLEAN:
                if isinstance(value, str):
                    return value.lower() in ("true", "1", "yes", "on")
                return bool(value)
            elif param_type == cls.STRING:
                return str(value)
            elif param_type == cls.ARRAY:
                if isinstance(value, str):
                    return json.loads(value)
                return list(value)
            elif param_type == cls.OBJECT:
                if isinstance(value, str):
                    return json.loads(value)
                return dict(value)
            elif (
                param_type == cls.NULL
                and isinstance(value, str)
                and value.lower() == "null"
            ):
                return None
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            raise cls.CastingError(
                f"Cannot convert value '{value}' to {param_type}: {e}"
            )

        raise ValueError(f"Cannot convert value '{value}' to {param_type}")


class JsonSchema(BaseModel):
    type = "object"
    properties: dict = {}
    required: list[str] = []

    def add_property(
        self,
        name: str,
        prop_type: JsonSchemaTypes,
        description: Optional[str] = None,
        required: bool = False,
    ):
        property_def = {"type": prop_type.value}
        if description:
            property_def["description"] = description

        self.properties[name] = property_def

        if required:
            self.required.append(name)

        return self
