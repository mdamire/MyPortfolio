from .parsers import FunctionParser
from .assembler import FeatureSchemaAssembler
from .schema import JsonSchemaTypes


class FeatureContainer:
    assembler_class: FeatureSchemaAssembler = None

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
        self.schema_assembler = self._get_schema_assembler()

    def _call_function(self, func, **kwargs):
        raise self.ContainerError("Function call not implemented")

    def _get_function_metadata(self, func):
        return FunctionParser(func).function_metadata

    def _get_registry(self, registrations, key):
        if key in registrations:
            return registrations[key]
        raise self.FunctionNotFoundError(key)

    def _validate_parameters(self, func_metadata, kwargs):
        validated_params = {}
        for param_info in func_metadata.parameters:
            param_name = param_info.name
            param_type = param_info.type_hint

            if param_name in kwargs:
                try:
                    validated_params[param_name] = JsonSchemaTypes.cast_python_type(
                        kwargs[param_name], param_type
                    )
                except JsonSchemaTypes.CastingError as e:
                    raise self.ParameterTypeCastingError(func_metadata.name, param_name)
            elif param_info.required:
                raise self.ParameterNotFoundError(func_metadata.name, param_name)

        return validated_params

    def _get_schema_assembler(self) -> FeatureSchemaAssembler:
        if self.assembler_class is None:
            raise self.ContainerError("Schema class is not set")
        return self.assembler_class()

    def _get_definition_key(self, func, **extra):
        return func.__name__

    def register(self, func, **extra):
        function_metadata = FunctionParser(func).function_metadata
        data_dict = dict(metadata=function_metadata, **extra)
        self.schema_assembler.add_definition(data_dict)
        self.definitions[self._get_definition_key(func, **extra)] = data_dict

        return function_metadata

    def call(self, data_key, **kwargs):
        if data_key not in self.definitions:
            raise self.FunctionNotFoundError(data_key)

        data_dict = self.definitions[data_key]
        func_metadata = data_dict["metadata"]

        # validate parameters
        validated_params = {}
        for param_info in func_metadata.arguments:
            param_name = param_info.name
            param_type = param_info.json_type
            required = param_info.required

            if param_name in kwargs:
                try:
                    validated_params[param_name] = JsonSchemaTypes.cast_type(
                        kwargs[param_name], param_type
                    )
                except JsonSchemaTypes.CastingError as e:
                    raise self.ParameterTypeCastingError(func_metadata.name, param_name)
            elif required:
                raise self.ParameterNotFoundError(func_metadata.name, param_name)

        try:
            result = func_metadata.function(**validated_params)
        except Exception as e:
            raise self.FunctionCallError(func_metadata.name, e) from e

        # add result to schema
        result_schema = self.schema_assembler.build_call_result_schema(
            result, data_dict=data_dict
        )

        return result_schema
