from .tools import Primitives


class Composer:
    def __init__(self, primitives_list: list[Primitives]):
        self.primitives_list = primitives_list

    def _make_registry(self):
        self.tools_registry = None
        self.prompt_registry = None
        self.resource_registry = None
        for primitives in self.primitives_list:
            if primitives.tools_registry:
                self.tools_registry += primitives.tools_registry
            if primitives.prompt_registry:
                self.prompt_registry += primitives.prompt_registry
            if primitives.resource_registry:
                self.resource_registry += primitives.resource_registry

    def compose(self, prompt: str):
        return self.primitives_list[0].call(prompt)
