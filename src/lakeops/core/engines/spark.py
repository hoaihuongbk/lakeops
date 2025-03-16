from typing import Any, Dict, Optional

from .base import Engine


class SparkEngine(Engine):
    def __init__(self, spark_session):
        self.spark = spark_session

    def read(
        self,
        path: str,
        format: str = "delta",
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        reader = self.spark.read.format(format)
        if options:
            reader = reader.options(**options)

        ## If path is a storage path, use load, otherwise use table
        if self.is_storage_path(path):
            return reader.load(path)
        else:
            return reader.table(path)

    def write(
        self,
        data: Any,
        path: str,
        format: str = "delta",
        mode: str = "overwrite",
        options: Optional[Dict[str, Any]] = None,
    ):
        ## For iceberg, we need to use writeTo pyspark API
        if format == "iceberg":
            if self.is_storage_path(path):
                raise ValueError("""
                    Iceberg format does not support writing to a storage path, 
                    please use the table name instead e.g. local.db.table_a
                """)
            self.write_to_table(data, path, format, mode, options)
        elif not self.is_storage_path(path):
            # Incase the path is a schema/table name, we need to use writeTo pyspark API
            self.write_to_table(data, path, format, mode, options)
        else:
            writer = data.write.format(format).mode(mode)
            if options:
                writer = writer.options(**options)
            writer.save(path)

    def write_to_table(
        self,
        data: Any,
        table_name: str,
        format: str = "iceberg",
        mode: str = "overwrite",
        options: Optional[Dict[str, Any]] = None,
    ):
        # https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.writeTo.html
        writer = data.writeTo(table_name).using(format)
        if options:
            writer = writer.options(**options)
        if mode == "overwrite":
            writer.createOrReplace()
        else:
            writer.append()

    def execute(self, sql: str, **kwargs) -> Any:
        return self.spark.sql(sql)