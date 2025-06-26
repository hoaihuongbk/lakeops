import pytest
from unittest.mock import patch, Mock
import polars as pl
from lakeops.core.engines import TrinoEngine, TrinoEngineConfig


class TestTrinoEngine:
    @pytest.fixture
    def trino_engine(self):
        return TrinoEngine(
            TrinoEngineConfig(
                host="localhost",
                port=8080,
                user="test_user",
                catalog="test_catalog",
                schema="test_schema",
                password="test_password",
            ),
        )

    @patch("polars.read_database")
    def test_execute_query(self, mock_read_database, trino_engine):
        # Prepare mock data
        mock_df = pl.DataFrame({"id": [1, 2, 3], "value": ["a", "b", "c"]})
        mock_read_database.return_value = mock_df

        # Execute test
        result = trino_engine.execute("SELECT * FROM test_table")

        # Verify
        assert isinstance(result, pl.DataFrame)
        assert len(result) == 3
        mock_read_database.assert_called_once()

    @patch("polars.read_database")
    def test_execute_with_parameters(self, mock_read_database, trino_engine):
        result = trino_engine.execute(
            "SELECT * FROM test_table", iter_batches=True, batch_size=1000
        )

        # Verify parameters were passed correctly
        mock_read_database.assert_called_with(
            query="SELECT * FROM test_table",
            connection=trino_engine.connection,
            iter_batches=True,
            batch_size=1000,
        )

    @patch("polars.read_database")
    def test_trino_query_error(self, mock_read_database, trino_engine):
        mock_read_database.side_effect = Exception("Connection failed")

        with pytest.raises(Exception) as exc_info:
            result = trino_engine.execute("SELECT * FROM test_table")

        assert "Connection failed" in str(exc_info.value)
