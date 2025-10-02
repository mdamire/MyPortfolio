from copy import deepcopy

from pydantic import BaseModel

from .registry import MCPRegistry
from .schemas import JsonRpcRequest
from .logging import get_logger


class RPCRequestManager:
    class PrimitiveMethodPrefix:
        tools = "tools"
        resources = "resources"
        prompts = "prompts"

    def __init__(self, registry: MCPRegistry):
        self.registry = registry

    def _process_tools_request(self, method_type, cursor, rpc_params):
        if self.registry.tools_container is None:
            raise ValueError("Tools container is not initialized")
        if method_type == "list":
            return self.registry.tools_container.build_list_result_schema(cursor)
        elif method_type == "call":
            kwargs = rpc_params.get("arguments", {})
            return self.registry.tools_container.call(rpc_params["name"], **kwargs)
        else:
            raise ValueError(f"Invalid method type: {method_type}")

    def _process_resources_request(self, method_type, cursor, rpc_params):
        if self.registry.resource_container is None:
            raise ValueError("Resource container is not initialized")
        if method_type == "list":
            return self.registry.resource_container.build_list_result_schema(cursor)
        elif method_type == "templates/list":
            self.registry.resource_container.build_template_list_result_schema(cursor)
        elif method_type == "read":
            return self.registry.resource_container.call(rpc_params["uri"])
        else:
            raise ValueError(f"Invalid method type: {method_type}")

    def _process_prompts_request(self, method_type, cursor, rpc_params):
        if self.registry.prompt_container is None:
            raise ValueError("Prompt container is not initialized")
        if method_type == "list":
            return self.registry.prompt_container.build_list_result_schema(cursor)
        elif method_type == "get":
            kwargs = rpc_params.get("arguments", {})
            return self.registry.prompt_container.call(rpc_params["name"], **kwargs)
        else:
            raise ValueError(f"Invalid method type: {method_type}")

    def _get_processor_mapping(self):
        return {
            self.PrimitiveMethodPrefix.tools: self._process_tools_request,
            self.PrimitiveMethodPrefix.resources: self._process_resources_request,
            self.PrimitiveMethodPrefix.prompts: self._process_prompts_request,
        }

    def _pop_cursor_param(self, rpc_params):
        if "cursor" in rpc_params:
            cursor = rpc_params.pop("cursor")
            return cursor
        return None

    def _process_result(self, result):
        if isinstance(result, BaseModel):
            return result.model_dump()
        if type(result) not in [dict, type(None)]:
            raise ValueError(f"Invalid result type: {type(result)}")
        return result

    def process_request(self, rpc_request: JsonRpcRequest) -> dict | None:
        """It should return a rpc result object."""
        processor_mapping = self._get_processor_mapping()

        # log if notification
        if rpc_request.id is None:
            get_logger().info(f"Notification: {rpc_request.method}")
            return None

        # prepare processor
        method_name, method_type = rpc_request.method.split("/", 1)
        if method_name not in processor_mapping:
            raise ValueError(f"Invalid method name: {method_name}")
        processor = processor_mapping[method_name]
        params = deepcopy(rpc_request.params)
        cursor = self._pop_cursor_param(params)

        # process request
        result = processor(method_type, cursor, params)

        # process result
        result = self._process_result(result)

        return result
