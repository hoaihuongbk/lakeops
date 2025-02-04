from typing import Any, Dict, Optional

import polars as pl

from .base import Engine


class PolarsEngine(Engine):
    def read_table(
        self,
        path_or_table_name: str,
        format: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        if format == "delta":
            return pl.read_delta(path_or_table_name, delta_table_options=options)
        elif format == "parquet":
            return pl.read_parquet(path_or_table_name)
        elif format == "csv":
            return pl.read_csv(path_or_table_name)
        elif format == "json":
            return pl.read_json(path_or_table_name)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def write_table(
        self,
        data: Any,
        path: str,
        format: str,
        mode: str = "overwrite",
        options: Optional[Dict[str, Any]] = None,
    ):
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

    def write_to_table(
        self,
        data: Any,
        table_name: str,
        format: str,
        mode: str = "overwrite",
        options: Optional[Dict[str, Any]] = None,
    ):
        raise NotImplementedError("Polars does not support write_to_table")