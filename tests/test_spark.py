import pytest
import logging
from pyspark.sql import SparkSession
from lakeops import LakeOps
from lakeops.core.engines import SparkEngine, SparkConnectEngine
import socket
import os

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
    test_data = spark.createDataFrame([(1, "John"), (2, "Jane")], ["id", "name"])

    # Write data using LakeOps
    test_path = str(tmp_path / "test_table")
    logger.info(f"Writing Delta table to: {test_path}")
    lake_ops.write(test_data, test_path, format="delta")

    # Read data back using LakeOps
    logger.info("Reading Delta table")
    read_df = lake_ops.read(test_path, format="delta")

    # Verify data
    row_count = read_df.count()
    logger.info(f"Read {row_count} rows from Polars Delta table")
    assert row_count == 2
    assert read_df.collect() == test_data.collect()


def test_read_write_iceberg(spark, lake_ops, tmp_path):
    logger.info(f"Using temporary directory: {tmp_path}")

    # Create test data
    test_data = spark.createDataFrame([(1, "Alice"), (2, "Bob")], ["id", "name"])

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
    row_count = read_df.count()
    logger.info(f"Read {row_count} rows from Polars Delta table")
    assert row_count == 2
    assert read_df.collect() == test_data.collect()


def is_port_open(host, port):
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except Exception:
        return False


@pytest.fixture(scope="module")
def spark_connect():
    # Default Spark Connect server is sc://localhost:15002
    # pyspark SparkSession.builder.remote('sc://localhost') uses port 15002
    if not is_port_open("localhost", 15002):
        pytest.skip("Spark Connect server is not running on localhost:15002")
    engine = SparkConnectEngine(remote_host="sc://localhost")
    return engine.spark


@pytest.fixture(scope="module")
def lake_ops_connect(spark_connect):
    engine = SparkConnectEngine(remote_host="sc://localhost")
    return LakeOps(engine)


def test_connect_read_write_delta(spark_connect, lake_ops_connect, tmp_path):
    # This test is similar to test_read_write_delta but uses SparkConnectEngine
    test_data = spark_connect.createDataFrame([(1, "John"), (2, "Jane")], ["id", "name"])
    test_path = str(tmp_path / "test_connect_table")
    lake_ops_connect.write(test_data, test_path, format="delta")
    read_df = lake_ops_connect.read(test_path, format="delta")
    assert read_df.count() == 2
    assert read_df.collect() == test_data.collect()


def test_connect_execute_sql(spark_connect, lake_ops_connect):
    # Simple SQL execution test
    df = lake_ops_connect.execute("SELECT 1 AS value")
    rows = df.collect()
    assert rows[0][0] == 1

