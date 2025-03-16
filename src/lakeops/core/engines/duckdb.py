from typing import Any, Dict, Optional
from .base import Engine

class DuckDBEngine(Engine):
    def __init__(self, path: str = ":memory:"):
        import duckdb
        self.duckdb = duckdb
        self.conn = duckdb.connect(path)

    def read(
        self, path: str, format: str = "delta", options: Optional[Dict[str, Any]] = None
    ) -> Any:
        raise NotImplementedError("DuckDBEngine does not support read_table")

    def write(
        self,
        data: Any,
        path: str,
        format: str = "delta",
        mode: str = "overwrite",
        options: Optional[Dict[str, Any]] = None,
    ) -> None:
        raise NotImplementedError("DuckDBEngine does not support write_table")

    def execute(self, sql: str, **kwargs) -> Any:
        return self.conn.execute(sql).pl()