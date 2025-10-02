from typing import List, Optional, Tuple, Any
from .pagination import Pagination


class FeatureSchemaAssembler:
    def __init__(self, page_size: int = 10):
        self.page_size = page_size
        self.pagination = Pagination(page_size)

    class SchemaAssemblerError(Exception):
        pass

    class EmptyResultError(SchemaAssemblerError):
        pass

    class SchemaAssemblerNotImplementedError(SchemaAssemblerError, NotImplementedError):
        pass

    class UnsupportedResultTypeError(SchemaAssemblerError):
        pass

    def _build_non_none_dict(self, schema):
        return {k: v for k, v in schema.model_dump().items() if v is not None}

    def _append_sorted_list(
        self, target_list: list, obj: dict | object, sort_key_name: str
    ):
        sort_key = (
            lambda x: x[sort_key_name]
            if isinstance(x, dict)
            else getattr(x, sort_key_name)
        )

        target_list.append(obj)
        target_list.sort(key=sort_key)

    def add_definition(self, data_dict):
        raise self.SchemaAssemblerNotImplementedError("add_definition")

    def build_list_result_schema(self):
        raise self.SchemaAssemblerNotImplementedError("build_list_result_schema")

    def process_call_result(self, result):
        raise self.SchemaAssemblerNotImplementedError("build_call_result")
