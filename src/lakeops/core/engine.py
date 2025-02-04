import pyarrow as pa
import polars as pl
from pyspark.sql import DataFrame
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class Engine(ABC):
    @abstractmethod
    def read_table(
        self,
        path_or_table_name: str,
        format: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> pl.DataFrame:
        pass

    @abstractmethod
    def write_table(
        self,
        data: pl.DataFrame,
        path: str,
        format: str,
        mode: str = "overwrite",
        options: Optional[Dict[str, Any]] = None,
    ) -> None:
        pass

    @abstractmethod
    def write_to_table(
        self,
        data: pl.DataFrame,
        table_name: str,
        format: str,
        mode: str = "overwrite",
        options: Optional[Dict[str, Any]] = None,
    ) -> None:
        pass


class SparkEngine(Engine):
    def __init__(self, spark_session):
        self.spark = spark_session

    def _convert_to_spark_df(self, data: pl.DataFrame) -> DataFrame:
        # Convert Polars DataFrame to Spark DataFrame via Arrow
        self.spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
        return self.spark.createDataFrame(data.to_pandas())

    def _covert_to_polars_df(self, spark_df: DataFrame) -> pl.DataFrame:
        # Convert Spark DataFrame to Polars DataFrame via Arrow
        # https://stackoverflow.com/questions/73203318/how-to-transform-spark-dataframe-to-polars-dataframe
        # spark-memory -> arrow/polars-memory
        return pl.from_arrow(pa.Table.from_batches(spark_df._collect_as_arrow()))

    def read_table(
        self,
        path_or_table_name: str,
        format: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> pl.DataFrame:
        reader = self.spark.read.format(format)
        if options:
            reader = reader.options(**options)

        spark_df = reader.load(path_or_table_name)
        return self._covert_to_polars_df(spark_df)

    def write_table(
        self,
        data: pl.DataFrame,
        path: str,
        format: str,
        mode: str = "overwrite",
        options: Optional[Dict[str, Any]] = None,
    ):
        spark_df = self._convert_to_spark_df(data)

        writer = spark_df.write.format(format).mode(mode)
        if options:
            writer = writer.options(**options)
        writer.save(path)

    def write_to_table(
        self,
        data: pl.DataFrame,
        table_name: str,
        format: str,
        mode: str = "overwrite",
        options: Optional[Dict[str, Any]] = None,
    ):
        # https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.writeTo.html
        spark_df = self._convert_to_spark_df(data)

        writer = spark_df.writeTo(table_name).using(format)
        if options:
            writer = writer.options(**options)
        if mode == "overwrite":
            writer.createOrReplace()
        else:
            writer.append()


class PolarsEngine(Engine):
    def read_table(
        self,
        path_or_table_name: str,
        format: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> pl.DataFrame:
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
        data: pl.DataFrame,
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