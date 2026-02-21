import pytest
import logging
from lakeops import LakeOps
from lakeops.core.engines import SparkEngine

pytestmark = pytest.mark.spark

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

