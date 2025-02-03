from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class Engine(ABC):
    @abstractmethod
    def read_table(
        self,
        path_or_table_name: str,
        format: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        pass

    @abstractmethod
    def write_table(
        self,
        data: Any,
        path: str,
        format: str,
        mode: str = "overwrite",
        options: Optional[Dict[str, Any]] = None,
    ) -> None:
        pass

    @abstractmethod
    def write_to_table(
        self,
        data: Any,
        table_name: str,
        format: str,
        mode: str = "overwrite",
        options: Optional[Dict[str, Any]] = None,
    ) -> None:
        pass


class SparkEngine(Engine):
    def __init__(self, spark_session):
        self.spark = spark_session

    def read_table(
        self,
        path_or_table_name: str,
        format: str,
        options: Optional[Dict[str, Any]] = None,
    ):
        reader = self.spark.read.format(format)
        if options:
            reader = reader.options(**options)
        return reader.load(path_or_table_name)

    def write_table(
        self,
        data: Any,
        path: str,
        format: str,
        mode: str = "overwrite",
        options: Optional[Dict[str, Any]] = None,
    ):
        writer = data.write.format(format).mode(mode)
        if options:
            writer = writer.options(**options)
        writer.save(path)

    def write_to_table(
        self,
        data: Any,
        table_name: str,
        format: str,
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
