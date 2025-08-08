import pytest
from unittest.mock import patch, MagicMock
from lakeops.core.engines.spark_connect import SparkConnectEngine


@patch("pyspark.sql.SparkSession")
def test_spark_connect_engine_init(MockSparkSession):
    """Test that the SparkConnectEngine is initialized correctly."""
    # Arrange
    mock_spark_session = MagicMock()
    MockSparkSession.builder.remote.return_value.getOrCreate.return_value = mock_spark_session

    # Act
    engine = SparkConnectEngine(remote_host="sc://some-host")

    # Assert
    MockSparkSession.builder.remote.assert_called_once_with("sc://some-host")
    assert engine.spark == mock_spark_session
