"""
JSON-RPC 2.0 serializers for handling request and response data.
"""

import json
from pydantic import ValidationError

from .schemas import JsonRpcRequest, JsonRpcSuccessResponse, JsonRpcErrorResponse
from .registry import MCPRegistry
from .managers import RPCRequestManager


class JsonRpcSerializer:
    """Serializer for JSON-RPC 2.0 requests."""

    def __init__(self, registry: MCPRegistry):
        self.registry = registry

    def validate(self, request_data):
        if isinstance(request_data, str):
            request_data = json.loads(request_data)

        if isinstance(request_data, list):
            for item in request_data:
                if not isinstance(item, dict):
                    raise ValueError("Invalid request data")
        elif not isinstance(request_data, dict):
            raise ValueError("Invalid request data")

        return request_data

    def _deserialize_request(self, request_data: dict) -> JsonRpcRequest:
        try:
            if isinstance(request_data, list):
                deserialized_data = []
                for item in request_data:
                    deserialized_data.append(JsonRpcRequest(**item))
                return deserialized_data
            else:
                return JsonRpcRequest(**request_data)
        except ValidationError as e:
            raise ValueError(f"Invalid JSON-RPC 2.0 request: {e}")

    def _build_single_rpc_response(self, rpc_request_data):
        rpc_request_manager = RPCRequestManager(self.registry)
        result_data = rpc_request_manager.process_request(rpc_request_data)
        return JsonRpcSuccessResponse(
            id=rpc_request_data.id, result=result_data
        ).model_dump()

    def _build_rpc_response(self, rpc_request_data):
        if isinstance(rpc_request_data, list):
            response_dict_list = []
            for item in rpc_request_data:
                try:
                    response_dict = self._build_single_rpc_response(item)
                except Exception as e:
                    response_dict = JsonRpcErrorResponse(
                        id=item.id, error=e
                    ).model_dump()
                response_dict_list.append(response_dict)

            # remove any None responses
            response_dict_list = [
                response_dict for response_dict in response_dict_list if response_dict
            ]
            response = response_dict_list or None
            return response
        else:
            try:
                response = self._build_single_rpc_response(rpc_request_data)
            except Exception as e:
                response = JsonRpcErrorResponse(
                    id=rpc_request_data.id, error=e
                ).model_dump()
            return response

    def process_request(self, request_data: dict):
        try:
            request_data = self.validate(request_data)
        except Exception as e:
            return JsonRpcErrorResponse(id=None, error=e).model_dump()

        try:
            data = self._deserialize_request(request_data)
        except Exception as e:
            return JsonRpcErrorResponse(id=None, error=e).model_dump()

        response = self._build_rpc_response(data)
        return response
