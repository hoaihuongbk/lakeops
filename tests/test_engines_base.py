from lakeops.core.engines.base import Engine


class DummyEngine(Engine):
    def read(self, path: str, format: str = "delta", options=None):
        return path, format, options

    def write(
        self,
        data,
        path: str,
        format: str = "delta",
        mode: str = "overwrite",
        options=None,
    ):
        return data, path, format, mode, options

    def execute(self, sql: str, **kwargs):
        return sql, kwargs


def test_is_storage_path():
    engine = DummyEngine()
    assert engine.is_storage_path("s3://bucket/table")
    assert engine.is_storage_path("/tmp/file.parquet")
    assert not engine.is_storage_path("table_name_only")

