import pytest
import logging
import polars as pl
from polars.testing import assert_frame_equal
from pyspark.sql import SparkSession
from lakeops import LakeOps
from lakeops.core.engine import SparkEngine

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
def spark():
    return (
        SparkSession.builder.appName("LakeOpsTest")
        .master("local[1]")
        .config(
            "spark.jars.packages",
            "io.delta:delta-spark_2.12:3.3.0,org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.6.1",
        )
        .config(
            "spark.sql.extensions",
            "io.delta.sql.DeltaSparkSessionExtension,org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
        )
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
        .getOrCreate()
    )


@pytest.fixture
def lake_ops(spark):
    engine = SparkEngine(spark)
    return LakeOps(engine)


def test_read_write_delta(spark, lake_ops, tmp_path):
    logger.info(f"Using temporary directory: {tmp_path}")

    # Create test data using Polars
    test_data = pl.DataFrame({
        "id": [1, 2],
        "name": ["John", "Jane"]
    })

    # Write data using LakeOps
    test_path = str(tmp_path / "test_table")
    logger.info(f"Writing Delta table to: {test_path}")
    lake_ops.write(test_data, test_path, format="delta")

    # Read data back using LakeOps
    logger.info("Reading Delta table")
    read_df = lake_ops.read(test_path, format="delta")

    # Verify data
    row_count = read_df.shape[0]
    logger.info(f"Read {row_count} rows from Polars Delta table")
    assert row_count == 2
    assert_frame_equal(read_df, test_data)


def test_read_write_iceberg(spark, lake_ops, tmp_path):
    logger.info(f"Using temporary directory: {tmp_path}")

    # Create test data
    test_data = pl.DataFrame({
        "id": [1, 2],
        "name": ["Alice", "Bob"]
    })

    # Write data using LakeOps
    # Use proper Iceberg table path with catalog
    table_name = "local.db.test_table"

    # Set required Spark configurations for Iceberg
    spark.conf.set("spark.sql.catalog.local", "org.apache.iceberg.spark.SparkCatalog")
    spark.conf.set("spark.sql.catalog.local.type", "hadoop")
    spark.conf.set("spark.sql.catalog.local.warehouse", f"{tmp_path}")

    logger.info(f"Writing Iceberg table name: {table_name}")
    lake_ops.write(
        test_data,
        table_name,
        format="iceberg",
        options={"write.format.default": "parquet"},
    )

    # Read data back using LakeOps
    logger.info("Reading Iceberg table")
    read_df = lake_ops.read(table_name, format="iceberg")

    # Verify data
    row_count = read_df.shape[0]
    logger.info(f"Read {row_count} rows from Polars Delta table")
    assert row_count == 2
    assert_frame_equal(read_df, test_data)

