import pytest
import logging
import polars as pl
from polars.testing import assert_frame_equal
from lakeops import LakeOps

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def lake_ops():
    return LakeOps()


def test_read_write_delta(lake_ops, tmp_path):
    logger.info(f"Using temporary directory: {tmp_path}")

    # Create test data
    test_data = pl.DataFrame(
        {
            "id": [1, 2],
            "name": ["John", "Jane"],
        }
    )

    # Write data using LakeOps
    test_path = str(tmp_path / "test_table")
    logger.info(f"Writing Polars Delta table to: {test_path}")
    lake_ops.write(test_data, test_path, format="delta")

    # Read data back using LakeOps
    logger.info("Reading Polars Delta table")
    read_df = lake_ops.read(test_path, format="delta")

    # Verify data
    row_count = read_df.shape[0]
    logger.info(f"Read {row_count} rows from Polars Delta table")
    assert row_count == 2
    assert_frame_equal(read_df, test_data)
