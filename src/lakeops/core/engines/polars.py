from typing import Any, Dict, Optional

import polars as pl

from .base import Engine


class PolarsEngine(Engine):
    def read(
        self,
        path: str,
        format: str = "delta",
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        if not self.is_storage_path(path):
            raise ValueError("PolarsEngine only supports reading from storage path")

        if format == "delta":
            return pl.read_delta(path, delta_table_options=options)
        elif format == "parquet":
            return pl.read_parquet(path)
        elif format == "csv":
            return pl.read_csv(path)
        elif format == "json":
            return pl.read_json(path)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def write(
        self,
        data: Any,
        path: str,
        format: str = "delta",
        mode: str = "overwrite",
        options: Optional[Dict[str, Any]] = None,
    ):
        if not self.is_storage_path(path):
            raise ValueError("PolarsEngine only supports writing to storage path")

        if format == "delta":
            data.write_delta(path, mode=mode, delta_write_options=options)
        elif format == "parquet":
            data.write_parquet(path)
        elif format == "csv":
            data.write_csv(path)
        elif format == "json":
            data.write_json(path)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def execute(self, sql: str, **kwargs) -> Any:
        raise NotImplementedError("PolarsEngine does not support execute SQL directly")
