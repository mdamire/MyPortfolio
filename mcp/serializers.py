class MCPSerializer:
    def __init__(
        self,
        data: dict,
        initializer,
        tools_registry,
        prompt_registry,
        resource_registry,
    ):
        self.data = data
        self.initializer = initializer
        self.tools_registry = tools_registry
        self.prompt_registry = prompt_registry
        self.resource_registry = resource_registry
        self.serialized_data = {}

    def serialize(self):
        return self.serialized_data
