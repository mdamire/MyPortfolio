from functools import wraps
import inspect

from .rpc import JsonSchemaTypes


class ParameterDefinition:
    def __init__(self, name: str, param_type: JsonSchemaTypes, required: bool):
        self.name = name
        self.param_type = param_type
        self.required = required


class FunctionDefinition:
    def __init__(self, func):
        self.func = func
        self.parameters = []

    def add_parameter(self, name: str, param_type: JsonSchemaTypes, required: bool):
        self.parameters.append(ParameterDefinition(name, param_type, required))


class FeatureSchemaAssembler:
    class SchemaAssemblerError(Exception):
        pass

    class SchemaAssemblerNotImplementedError(SchemaAssemblerError, NotImplementedError):
        pass

    def add_function_definition(self, func, **extra):
        raise self.SchemaAssemblerNotImplementedError("add_function_definition")

    def add_call_result(self, result: dict):
        raise self.SchemaAssemblerNotImplementedError("add_call_result")

    def build_list_result_schema(self):
        raise self.SchemaAssemblerNotImplementedError("build_list_result_schema")

    def build_call_result_schema(self):
        raise self.SchemaAssemblerNotImplementedError("build_call_result_schema")


class FeatureContainer:
    schema_class: FeatureSchemaAssembler = None

    class ContainerError(Exception):
        pass

    class FunctionNotFoundError(Exception):
        def __init__(self, func_name: str):
            self.func_name = func_name
            super().__init__(f"Function '{func_name}' not found")

    class ParameterNotFoundError(Exception):
        def __init__(self, func_name: str, param_name: str):
            self.func_name = func_name
            self.param_name = param_name
            super().__init__(
                f"Parameter '{param_name}' not found in function '{func_name}'"
            )

    class ParameterTypeCastingError(Exception):
        def __init__(self, func_name: str, param_name: str):
            self.func_name = func_name
            self.param_name = param_name
            super().__init__(
                f"Parameter '{param_name}' casting error in function '{func_name}'"
            )

    class FunctionCallError(Exception):
        def __init__(self, func_name: str, error: Exception):
            self.func_name = func_name
            self.error = error
            super().__init__(f"Error calling function '{func_name}': {error}")

    def __init__(self):
        self.definitions = {}
        self.schema = self.get_schema()

    def get_schema(self) -> FeatureSchemaAssembler:
        if self.schema_class is None:
            raise self.ContainerError("Schema class is not set")
        return self.schema_class()

    def register(self, **extra):
        def decorator(func):
            name = func.__name__

            function_definition = FunctionDefinition(func)
            self.schema.add_function_definition(func, **extra)

            sig = inspect.signature(func)
            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue

                required = param.default == inspect.Parameter.empty
                param_type = JsonSchemaTypes.from_python_type(param.annotation)
                function_definition.add_parameter(param_name, param_type, required)

            self.definitions[name] = function_definition

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    def call(self, func_name, **kwargs):
        if func_name not in self.definitions:
            raise self.FunctionNotFoundError(func_name)

        func_def = self.definitions[func_name]

        validated_params = {}
        for param_info in func_def.parameters:
            param_name = param_info.name
            param_type = param_info.param_type
            required = param_info.required

            if param_name in kwargs:
                try:
                    validated_params[param_name] = JsonSchemaTypes.cast_type(
                        kwargs[param_name], param_type
                    )
                except JsonSchemaTypes.CastingError as e:
                    raise self.ParameterTypeCastingError(func_name, param_name)
            elif required:
                raise self.ParameterNotFoundError(func_name, param_name)

        try:
            result = func_def.func(**validated_params)
        except Exception as e:
            raise self.FunctionCallError(func_name, e)

        # add result to schema
        self.schema.add_call_result(result)  # pyright: ignore[reportUnreachable]

        return result
