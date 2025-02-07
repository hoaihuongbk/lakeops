from typing import Any, Dict, Optional

from .engines import Engine, PolarsEngine


class LakeOps:
    """
    LakeOps provides methods for user management including creation, read and write
    dataset from/to a datalake through a storage path or schema/table name.
    """

    def __init__(self, engine: Optional[Engine] = None):
        self.engine = engine or PolarsEngine()

    def read(
        self,
        path_or_table_name: str,
        format: str = "delta",
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Read a table from a storage path or schema/table name.

        Args:
            path_or_table_name: Storage path or schema/table name to read from
            format: Table format (default: 'delta')
            options: Additional options to pass to the underlying engine

        Returns:
            pyspark.sql.DataFrame: If using SparkEngine
            polars.DataFrame: If using PolarsEngine (default)
        """
        return self.engine.read_table(path_or_table_name, format, options)
    def write(
        self,
        data: Any,
        path_or_table_name: str,
        format: str = "delta",
        mode: str = "overwrite",
        options: Optional[Dict[str, Any]] = None,
    ):
        """Write a table to a storage path or schema/table name.

        Args:
            data: Data to write (DataFrame)
            path_or_table_name: Storage path or schema/table name to write to
            format: Table format (default: 'delta')
            mode: Write mode - 'overwrite', 'append', etc. (default: 'overwrite')
            options: Additional options to pass to the underlying engine

        Returns:
            None
        """
        if "/" not in path_or_table_name:
            return self.engine.write_to_table(
                data, path_or_table_name, format, mode, options
            )

        if format == "iceberg":
            raise ValueError("Table name must be provided for Iceberg format")

        return self.engine.write_table(data, path_or_table_name, format, mode, options)


    def execute(self, sql: str, **kwargs) -> Any:
        """Execute a SQL query and return the result.
        Args:
            sql: SQL query to execute
            **kwargs: Additional arguments to pass to the underlying engine

        Returns:
            pyspark.sql.DataFrame: If using SparkEngine
            polars.DataFrame: If using PolarsEngine (default) or TrinoEngine
        """
        return self.engine.execute(sql, **kwargs)
