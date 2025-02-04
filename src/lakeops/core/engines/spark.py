from typing import Any, Dict, Optional

import polars as pl
import pyarrow as pa
from pyspark.sql import DataFrame

from .base import Engine


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