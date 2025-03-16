import pytest
from lakeops.core.engines.duckdb import DuckDBEngine


class TestDuckDBEngine:
    def test_init(self):
        # Test engine initialization
        engine = DuckDBEngine(path=":memory:")
        assert isinstance(engine, DuckDBEngine)

    def test_read_not_implemented(self):
        # Test that read method raises NotImplementedError
        engine = DuckDBEngine(path=":memory:")
        with pytest.raises(NotImplementedError) as excinfo:
            engine.read(path="test_path", format="delta")
        assert "DuckDBEngine does not support read_table" in str(excinfo.value)

    def test_write_not_implemented(self):
        # Test that write method raises NotImplementedError
        engine = DuckDBEngine(path=":memory:")
        with pytest.raises(NotImplementedError) as excinfo:
            engine.write(data=None, path="test_path", format="delta")
        assert "DuckDBEngine does not support write_table" in str(excinfo.value)

    def test_execute(self):
        # Test that execute method properly runs SQL
        engine = DuckDBEngine(path=":memory:")
        result = engine.execute("SELECT 1 AS value")
        # Assuming the result is a polars DataFrame
        assert result is not None
        assert "value" in result.columns
        assert result.shape[0] == 1
        assert result["value"][0] == 1
