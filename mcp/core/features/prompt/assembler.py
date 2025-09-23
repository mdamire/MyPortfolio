from .schema import PromptDefinitionSchema, PromptsListSchema, PromptResultSchema
from ..base.assembler import FeatureSchemaAssembler
from ..base.schema import JsonSchemaTypes
from pydantic import BaseModel
from .contents import PromptsContent


class PromptsSchemaAssembler(FeatureSchemaAssembler):
    def __init__(self):
        self.prompts_list = []

    def add_resource_registry(self, registry):
        metadata = registry["metadata"]

        # Create arguments schema from function parameters
        arguments_schema = self._create_arguments_schema(metadata)

        # Build definition schema
        definition_schema = PromptDefinitionSchema(
            name=registry.get("name") or metadata.name,
            title=registry.get("title") or metadata.title,
            description=registry.get("description") or metadata.description,
            arguments=arguments_schema,
        )

        # Convert to dict and add to prompts list
        self.prompts_list.append(self._build_non_none_dict(definition_schema))
        return definition_schema

    def _create_arguments_schema(self, metadata):
        """Create arguments schema from function arguments."""
        if not metadata.arguments:
            return None

        arguments = []
        for arg in metadata.arguments:
            json_type = JsonSchemaTypes.from_python_type(arg.type_hint)
            arg_schema = {
                "name": arg.name,
                "type": json_type,
                "description": arg.description,
                "required": arg.required,
            }
            arguments.append(arg_schema)

        return arguments

    def build_list_result_schema(self):
        """Build the list result schema for prompts."""
        return PromptsListSchema(prompts=self.prompts_list).model_dump()

    def process_result(self, result:PromptsContent, registry:dict={}):
        """Process the result from prompt function calls."""
        if not isinstance(result, PromptsContent):
            raise self.UnsupportedResultTypeError(
                f"Unsupported result type: {type(result)}"
            )
        
        result_schema = PromptResultSchema(
            description=result.description or registry.get("description"),
            messages=result.messages,
        )
        return result_schema.model_dump()
