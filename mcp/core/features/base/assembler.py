class FeatureSchemaAssembler:
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

    def add_definition(self, data_dict):
        raise self.SchemaAssemblerNotImplementedError("add_definition")

    def build_list_result_schema(self):
        raise self.SchemaAssemblerNotImplementedError("build_list_result_schema")

    def process_call_result(self, result):
        raise self.SchemaAssemblerNotImplementedError("build_call_result")
