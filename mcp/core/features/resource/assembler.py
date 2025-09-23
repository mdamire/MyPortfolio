from .schema import (
    ResourceListResultSchema,
    ResourceTemplateListResultSchema,
    ResourceDefinitionSchema,
    TextContentSchema,
    BinaryContentSchema,
)
from ..base.assembler import FeatureSchemaAssembler
from .contents import ResourceContent, TextContent, BinaryContent, ContentSchema


class ResourceSchemaAssembler(FeatureSchemaAssembler):
    def __init__(self):
        self.resource_list = []
        self.resource_template_list = []

    def add_resource_registry(self, resource_registry):
        from .container import FunctionRegistry

        if (
            isinstance(resource_registry, FunctionRegistry)
            and resource_registry.metadata.has_required_arguments
        ):
            self.resource_template_list.append(resource_registry)
        else:
            self.resource_list.append(resource_registry)

    def _build_definition_schema(self, resource_registry_list):
        from .container import FunctionRegistry

        resource_schema_list = []
        for resource_registry in resource_registry_list:
            if isinstance(resource_registry, FunctionRegistry):
                metadata = resource_registry.metadata

                # build definition schema
                definition_schema = ResourceDefinitionSchema(
                    uri=resource_registry.uri,
                    name=resource_registry.extra.get("name") or metadata.name,
                    title=resource_registry.extra.get("title") or metadata.title,
                    description=resource_registry.extra.get("description")
                    or metadata.description,
                    mimeType=resource_registry.extra.get("mimeType")
                    or metadata.mimeType,
                    size=resource_registry.extra.get("size"),
                    annotations=resource_registry.extra.get("annotations"),
                )
            else:
                definition_schema = ResourceDefinitionSchema(
                    uri=resource_registry.uri,
                    name=resource_registry.extra.get("name"),
                    title=resource_registry.extra.get("title"),
                    description=resource_registry.extra.get("description"),
                    mimeType=resource_registry.extra.get("mimeType"),
                    size=resource_registry.extra.get("size"),
                    annotations=resource_registry.extra.get("annotations"),
                )

            # add metadata to definition_schema
            resource_schema_list.append(self._build_non_none_dict(definition_schema))

        return resource_schema_list

    def build_list_result_schema(self):
        resource_schema_list = self._build_definition_schema(self.resource_list)
        schema = ResourceListResultSchema(resources=resource_schema_list).model_dump()
        return schema

    def build_template_list_result_schema(self):
        resource_template_schema_list = self._build_definition_schema(
            self.resource_template_list
        )
        schema = ResourceTemplateListResultSchema(
            resourceTemplates=resource_template_schema_list
        ).model_dump()
        return schema

    def process_content(self, resource_content, resource_registry):
        if not isinstance(resource_content, ResourceContent):
            raise self.UnsupportedResultTypeError(
                f"Unsupported result type: {type(resource_content)}"
            )

        content_schema_list = []
        for content in resource_content.content_list:
            schema_data = {
                "uri": content.uri or resource_registry.uri,
                "name": content.name or resource_registry.extra.get("name"),
                "title": content.title or resource_registry.extra.get("title"),
                "mimeType": content.mime_type
                or resource_registry.extra.get("mimeType"),
                "annotations": content.annotations
                or resource_registry.extra.get("annotations"),
            }

            if isinstance(content, TextContent):
                schema = TextContentSchema(
                    text=content.text,
                    **schema_data,
                )
            elif isinstance(content, BinaryContent):
                schema = BinaryContentSchema(
                    blob=content.blob,
                    **schema_data,
                )

            content_schema_list.append(self._build_non_none_dict(schema))

        content_schema = ContentSchema(contents=content_schema_list)
        return content_schema.model_dump()
