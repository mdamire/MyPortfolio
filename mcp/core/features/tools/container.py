from ..base.container import FeatureContainer
from .assembler import ToolsSchemaAssembler


class ToolsContainer(FeatureContainer):
    def __init__(self):
        self.schema_assembler = ToolsSchemaAssembler()
        self.registrations = {}

    def register(self, func, **extra):
        function_metadata = self._get_function_metadata(func)
        registry_data = dict(metadata=function_metadata, **extra)
        self.schema_assembler.add_resource_registry(registry_data)
        self.registrations[func.__name__] = registry_data
        return function_metadata
    
    def build_list_result_schema(self):
        return self.schema_assembler.build_list_result_schema()

    def call(self, func_name, **kwargs):
        registry = self._get_registry(self.registrations, func_name)
        func_metadata = registry["metadata"]
        validated_params = self._validate_parameters(func_metadata, kwargs)
        result = self._call_function(func_metadata.function, **validated_params)
        return self.schema_assembler.process_result(result)
