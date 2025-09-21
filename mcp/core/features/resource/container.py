from ..base.container import FeatureContainer
from .assembler import ResourceSchemaAssembler
from ..base.parsers import FunctionParser
from .contents import ResourceContent


class ContentRegistry():
    def __init__(self, content, uri, extra: dict):
        self.content = content
        self.uri = uri
        self.extra = extra

class FunctionRegistry():
    def __init__(self, metadata, uri, extra: dict):
        self.metadata = metadata
        self.uri = uri
        self.extra = extra

class ResourceContainer(FeatureContainer):
    content_key = "content"
    function_key = "function"

    def __init__(self):
        self.schema_assembler = ResourceSchemaAssembler()
        self.registrations = {}

    def add_resource(self, uri, **extra):
        resource_content = ResourceContent()
        registry = ContentRegistry(resource_content, uri, extra)
        self.schema_assembler.add_resource_registry(registry)
        self.registrations[uri] = registry
        return registry

    def register(self, func, uri, **extra):
        function_metadata = FunctionParser(func).function_metadata
        registry = FunctionRegistry(function_metadata, uri, extra)
        self.schema_assembler.add_resource_registry(registry)
        self.registrations[uri] = registry

        return function_metadata

    def _parse_uri(self, uri: str):
        # If exact match exists, return it with empty params
        if uri in self.registrations:
            return uri, []

        return_uri = None
        for saved_uri in sorted(self.registrations.keys()):
            if uri.startswith(saved_uri):
                return_uri = saved_uri
                break

        if not return_uri:
            raise self.FunctionNotFoundError(uri)

        # Extract parameters from remaining path
        remaining_path = uri[len(return_uri) :].strip("/")
        return_params = remaining_path.split("/") if remaining_path else []

        return return_uri, return_params

    def call(self, uri, **kwargs):
        parsed_uri, parsed_params = self._parse_uri(uri)
        registry = self._get_registry(self.registrations, parsed_uri)
        if isinstance(registry, ContentRegistry):
            processed_result = self.schema_assembler.process_content(registry.content, registry)
        
        result_content = self._call_function(registry.metadata.function, parsed_params, **kwargs)
        processed_result = self.schema_assembler.process_content(result_content, registry)
        return processed_result
