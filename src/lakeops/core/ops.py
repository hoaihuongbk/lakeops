from typing import Any, Dict, Optional

from .engines import Engine, PolarsEngine


class LakeOps:
    def __init__(self, engine: Optional[Engine] = None):
        self.engine = engine or PolarsEngine()

    def read(
        self,
        path_or_table_name: str,
        format: str = "delta",
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Read table from path"""
        return self.engine.read_table(path_or_table_name, format, options)

    def write(
        self,
        data: Any,
        path_or_table_name: str,
        format: str = "delta",
        mode: str = "overwrite",
        options: Optional[Dict[str, Any]] = None,
    ):
        """Write table to path"""
        if "/" not in path_or_table_name:
            return self.engine.write_to_table(
                data, path_or_table_name, format, mode, options
            )

        return self.engine.write_table(data, path_or_table_name, format, mode, options)
