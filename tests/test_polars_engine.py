import pytest

import lakeops.core.engines.polars as polars_mod
from lakeops.core.engines.polars import PolarsEngine


class DummyDataFrame:
    def __init__(self):
        self.calls = {}

    def write_delta(self, path, mode="overwrite", delta_write_options=None):
        self.calls["delta"] = (path, mode, delta_write_options)

    def write_parquet(self, path):
        self.calls["parquet"] = path

    def write_csv(self, path):
        self.calls["csv"] = path

    def write_json(self, path):
        self.calls["json"] = path


def test_polars_read_supported_formats(monkeypatch):
    calls = {}

    class FakePL:
        def read_delta(self, path, delta_table_options=None):
            calls["delta"] = (path, delta_table_options)
            return "DELTA_DF"

        def read_parquet(self, path):
            calls["parquet"] = path
            return "PARQUET_DF"

        def read_csv(self, path):
            calls["csv"] = path
            return "CSV_DF"

        def read_json(self, path):
            calls["json"] = path
            return "JSON_DF"

    monkeypatch.setattr(polars_mod, "pl", FakePL())

    engine = PolarsEngine()

    df_delta = engine.read("/tmp/table_delta", format="delta", options={"a": 1})
    df_parquet = engine.read("/tmp/table_parquet", format="parquet")
    df_csv = engine.read("/tmp/table_csv", format="csv")
    df_json = engine.read("/tmp/table_json", format="json")

    assert df_delta == "DELTA_DF"
    assert df_parquet == "PARQUET_DF"
    assert df_csv == "CSV_DF"
    assert df_json == "JSON_DF"

    assert calls["delta"] == ("/tmp/table_delta", {"a": 1})
    assert calls["parquet"] == "/tmp/table_parquet"
    assert calls["csv"] == "/tmp/table_csv"
    assert calls["json"] == "/tmp/table_json"


def test_polars_read_invalid_path_raises():
    engine = PolarsEngine()
    with pytest.raises(ValueError, match="only supports reading from storage path"):
        engine.read("logical_table_name", format="delta")


def test_polars_read_unsupported_format_raises():
    engine = PolarsEngine()
    with pytest.raises(ValueError, match="Unsupported format"):
        engine.read("/tmp/table_unknown", format="unknown")


def test_polars_write_supported_formats(monkeypatch):
    df = DummyDataFrame()
    engine = PolarsEngine()

    engine.write(df, "/tmp/out_delta", format="delta", mode="overwrite", options={"a": 1})
    engine.write(df, "/tmp/out_parquet", format="parquet")
    engine.write(df, "/tmp/out_csv", format="csv")
    engine.write(df, "/tmp/out_json", format="json")

    assert df.calls["delta"] == ("/tmp/out_delta", "overwrite", {"a": 1})
    assert df.calls["parquet"] == "/tmp/out_parquet"
    assert df.calls["csv"] == "/tmp/out_csv"
    assert df.calls["json"] == "/tmp/out_json"


def test_polars_write_invalid_path_raises():
    df = DummyDataFrame()
    engine = PolarsEngine()
    with pytest.raises(ValueError, match="only supports writing to storage path"):
        engine.write(df, "logical_table_name", format="delta")


def test_polars_write_unsupported_format_raises():
    df = DummyDataFrame()
    engine = PolarsEngine()
    with pytest.raises(ValueError, match="Unsupported format"):
        engine.write(df, "/tmp/out_unknown", format="unknown")


def test_polars_execute_not_implemented():
    engine = PolarsEngine()
    with pytest.raises(NotImplementedError, match="does not support execute SQL directly"):
        engine.execute("SELECT 1")

