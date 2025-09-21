import inspect
import re
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from primitives import FeatureContainer, FeatureSchemaAssembler

# add http resource
# resource


class ResourceDefinitionSchema(BaseModel):
    uri: str
    name: str
    title: Optional[str] = None
    description: Optional[str] = None
    mimeType: str
    size: Optional[int] = None
    annotations: Optional[dict] = None


class ResourceListResultSchema(BaseModel):
    resources: List[ResourceDefinitionSchema]


class ResourceTemplateListResultSchema(BaseModel):
    resourceTemplates: List[ResourceDefinitionSchema]


class ResourceSchemaAssembler(FeatureSchemaAssembler):
    def __init__(self):
        self.resource_list = []
        self.resource_template_list = []
        self.contents_list = []

    def _parse_docstring_title_description(self, docstring):
        """Parse docstring to extract title and description.
        Title is the first line if followed by empty line.
        Description is the rest after title.
        """
        if not docstring:
            return None, None

        lines = docstring.strip().split("\n")
        lines = [line.rstrip() for line in lines]

        title = None
        description = None

        # Check if first line is title (followed by empty line or end)
        if len(lines) > 1 and lines[1].strip() == "":
            title = lines[0].strip()
            # Description is everything after the empty line
            description_lines = []
            for line in lines[2:]:
                line = line.strip()
                if line:  # Skip empty lines within description
                    description_lines.append(line)
            description = " ".join(description_lines) if description_lines else None
        elif len(lines) == 1:
            title = lines[0].strip()
        else:
            # No title, treat entire docstring as description
            description_lines = []
            for line in lines:
                line = line.strip()
                if line:
                    description_lines.append(line)
            description = " ".join(description_lines) if description_lines else None

        return title, description

    def _extract_uri_parameters(self, uri):
        """Extract parameters from URI that are in braces like {param}."""
        return re.findall(r"\{(\w+)\}", uri)

    def add_function_definition(self, func, **extra):
        """Add function (resource) definition to schema."""

        # Extract function name
        name = func.__name__

        # Parse docstring for title and description
        title, description = self._parse_docstring_title_description(func.__doc__)

        # Collect all schema parameters
        schema_params = {
            "name": name,
            "title": title,
            "description": description,
            **extra,  # This includes uri, mimeType, size, annotations, etc.
        }

        # Create resource definition - let Pydantic validate required fields
        try:
            definition = ResourceDefinitionSchema(**schema_params)
        except Exception as e:
            raise ValueError(
                f"Invalid resource definition for function '{name}': {e}"
            ) from e

        # Check if URI has parameters in braces
        uri_params = self._extract_uri_parameters(definition.uri)

        # Get function signature to check required parameter count
        sig = inspect.signature(func)
        required_params = [
            param_name
            for param_name, param in sig.parameters.items()
            if param_name != "self" and param.default == inspect.Parameter.empty
        ]

        # Verify URI parameters match required function parameters
        if len(uri_params) != len(required_params):
            raise ValueError(
                f"URI template parameters {uri_params} must match "
                f"required function parameters {required_params}"
            )

        if uri_params:
            # Add to template list
            self.resource_template_list.append(definition)
        else:
            # Add to regular resource list
            self.resource_list.append(definition)

        return definition

    def add_call_result(self, result: dict):
        pass

    def build_list_result_schema(self):
        """Build schema for listing resources."""
        list_result = ResourceListResultSchema(resources=self.resource_list)
        return list_result.model_dump()

    def build_template_list_result_schema(self):
        list_result = ResourceTemplateListResultSchema(
            resourceTemplates=self.resource_template_list
        )
        return list_result.model_dump()

    def build_call_result_schema(self):
        """Build schema for resource call results."""
        call_result = {"contents": self.contents_list}

        # Clean up for next call
        self.contents_list = []

        return call_result


class ResourcesContainer(FeatureContainer):
    schema_class = ResourceSchemaAssembler
