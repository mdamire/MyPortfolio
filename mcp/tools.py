import inspect
import json
from functools import wraps
from .rpc import (
    ToolsSchema,
    ToolInputDefinitionSchema,
    SchemaTypes,
    SchemaTypeMappingError,
    PromptSchema,
    PromptArgumentDefinition,
)


class Initializer:
    pass


class Primitives:
    def __init__(self):
        self.tools_registry = ToolsRegistry()
        self.prompt_registry = PromptRegistry()
        self.resource_registry = ResourceRegistry()

    def register_tool(self, func):
        self.tools_registry.register(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper


class FunctionDefinition:
    def __init__(self, func):
        self.func = func
        self.parameters = []

    def add_parameter(self, name, param_type, required):
        self.parameters.append(
            {"name": name, "param_type": param_type, "required": required}
        )


class ToolsRegistry:
    def __init__(self):
        self.definitions = {}
        self.schema = ToolsSchema()

    def _cast_value(self, value, schema_type, param_name):
        """Cast a value to the appropriate type based on schema type"""
        try:
            if schema_type == SchemaTypes.INTEGER:
                return int(value)
            elif schema_type == SchemaTypes.NUMBER:
                return float(value)
            elif schema_type == SchemaTypes.BOOLEAN:
                if isinstance(value, str):
                    return value.lower() in ("true", "1", "yes", "on")
                return bool(value)
            elif schema_type == SchemaTypes.STRING:
                return str(value)
            elif schema_type == SchemaTypes.ARRAY:
                if isinstance(value, str):
                    return json.loads(value)
                return list(value)
            elif schema_type == SchemaTypes.OBJECT:
                if isinstance(value, str):
                    return json.loads(value)
                return dict(value)
            elif (
                schema_type == SchemaTypes.NULL
                and isinstance(value, str)
                and value.lower() == "null"
            ):
                return None
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            python_type_name = SchemaTypes.to_python_type(schema_type).__name__
            raise ValueError(
                f"Cannot convert parameter '{param_name}' to {python_type_name}: {e}"
            )

        raise ValueError(f"Cannot convert parameter '{param_name}' to {schema_type}")

    def register(self, func):
        # Extract function information
        name = func.__name__
        description = func.__doc__ or ""

        definition = FunctionDefinition(func)

        # Create input schema from function parameters
        input_schema = ToolInputDefinitionSchema()

        # Get function signature
        # sig.return_annotation return the type of the return value
        sig = inspect.signature(func)

        # Process each parameter
        for param_name, param in sig.parameters.items():
            # Skip self parameter
            if param_name == "self":
                continue

            # Determine if parameter is required
            required = param.default == inspect.Parameter.empty

            # Get type from param.annotation and convert to SchemaTypes
            python_type = (
                param.annotation if param.annotation != inspect.Parameter.empty else str
            )
            schema_type = SchemaTypes.from_python_type(python_type)

            # Add parameter to tool definition (store as SchemaTypes)
            definition.add_parameter(
                name=param_name,
                param_type=schema_type,  # Store SchemaTypes instead of Python type
                required=required,
            )

            # Add parameter to input schema
            input_schema.add_property(
                name=param_name, prop_type=schema_type, required=required
            )

        # Add definition to tools schema
        self.schema.add_definition(
            name=name, description=description, input_schema=input_schema
        )

        self.definitions[name] = definition

        return func

    def call_tool(self, tool_name, **kwargs):
        # Check if tool exists
        if tool_name not in self.definitions:
            raise ValueError(f"Tool '{tool_name}' not found")

        tool_def = self.definitions[tool_name]

        # Validate and type cast parameters
        validated_params = {}

        for param_info in tool_def.parameters:
            param_name = param_info["name"]
            schema_type = param_info["param_type"]  # This is now a SchemaTypes enum
            required = param_info["required"]

            # Check if required parameter is missing
            if required and param_name not in kwargs:
                raise ValueError(f"Missing required parameter: {param_name}")

            # If parameter is provided, type cast it
            if param_name in kwargs:
                value = kwargs[param_name]
                validated_params[param_name] = self._cast_value(
                    value, schema_type, param_name
                )

        # Call the function with validated parameters
        try:
            result = tool_def.func(**validated_params)
            return result
        except Exception as e:
            raise RuntimeError(f"Error calling tool '{tool_name}': {e}") from e


class PromptRegistry:
    def __init__(self):
        self.prompts = {}
        self.schema = PromptSchema()

    def _cast_value(self, value, schema_type, param_name):
        """Cast a value to the appropriate type based on schema type"""
        try:
            if schema_type == SchemaTypes.INTEGER:
                return int(value)
            elif schema_type == SchemaTypes.NUMBER:
                return float(value)
            elif schema_type == SchemaTypes.BOOLEAN:
                if isinstance(value, str):
                    return value.lower() in ("true", "1", "yes", "on")
                return bool(value)
            elif schema_type == SchemaTypes.STRING:
                return str(value)
            elif schema_type == SchemaTypes.ARRAY:
                if isinstance(value, str):
                    return json.loads(value)
                return list(value)
            elif schema_type == SchemaTypes.OBJECT:
                if isinstance(value, str):
                    return json.loads(value)
                return dict(value)
            elif (
                schema_type == SchemaTypes.NULL
                and isinstance(value, str)
                and value.lower() == "null"
            ):
                return None
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            python_type_name = SchemaTypes.to_python_type(schema_type).__name__
            raise ValueError(
                f"Cannot convert parameter '{param_name}' to {python_type_name}: {e}"
            )

        raise ValueError(f"Cannot convert parameter '{param_name}' to {schema_type}")

    def register(self, func):
        # Extract function information
        name = func.__name__
        description = func.__doc__ or ""

        # Create function definition
        definition = FunctionDefinition(func)

        # Create prompt arguments from function parameters
        arguments = PromptArgumentDefinition()

        # Get function signature
        sig = inspect.signature(func)

        # Process each parameter
        for param_name, param in sig.parameters.items():
            # Skip self parameter
            if param_name == "self":
                continue

            # Determine if parameter is required
            required = param.default == inspect.Parameter.empty

            # Get type from param.annotation for description
            param_description = None
            if param.annotation != inspect.Parameter.empty:
                param_description = f"Type: {param.annotation.__name__}"

            definition.add_parameter(
                name=param_name,
                param_type=SchemaTypes.from_python_type(str),
                required=required,
            )

            # Add argument to prompt arguments
            arguments.add_argument_definition(
                name=param_name, description=param_description, required=required
            )

        # Add prompt definition to schema
        self.schema.add_prompt_definition(
            name=name, description=description, arguments=arguments
        )

        # Store the function definition
        self.prompts[name] = definition

        return func

    def call(self, func_name, **kwargs):
        # Check if tool exists
        if func_name not in self.prompts:
            raise ValueError(f"Prompt '{func_name}' not found")

        func_def = self.prompts[func_name]

        # Validate and type cast parameters
        validated_params = {}

        for param_info in func_def.parameters:
            param_name = param_info["name"]
            schema_type = param_info["param_type"]  # This is now a SchemaTypes enum
            required = param_info["required"]

            # Check if required parameter is missing
            if required and param_name not in kwargs:
                raise ValueError(f"Missing required parameter: {param_name}")

            # If parameter is provided, type cast it
            if param_name in kwargs:
                value = kwargs[param_name]
                validated_params[param_name] = self._cast_value(
                    value, schema_type, param_name
                )

        # Call the function with validated parameters
        try:
            result = func_def.func(**validated_params)
            return result
        except Exception as e:
            raise RuntimeError(f"Error calling prompt '{func_name}': {e}") from e
