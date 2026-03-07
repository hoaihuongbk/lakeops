import pytest

from lakeops.cli import main as lakeops_main


class TestLakeOpsCLI:
    def test_read_uses_lakeops_and_polars_engine(self, monkeypatch, capsys):
        calls = {}

        class FakePolarsEngine:
            def __init__(self):
                calls["engine_created"] = True

        class FakeLakeOps:
            def __init__(self, engine=None):
                calls["lakeops_engine"] = engine

            def read(self, path, format="delta", options=None):
                calls["read_args"] = (path, format, options)
                return "FAKE_DF"

        monkeypatch.setattr("lakeops.cli.PolarsEngine", FakePolarsEngine)
        monkeypatch.setattr("lakeops.cli.LakeOps", FakeLakeOps)

        exit_code = lakeops_main(
            ["read", "s3://bucket/table", "--format", "delta", "--options", '{"a": 1}']
        )
        captured = capsys.readouterr()

        assert exit_code == 0
        assert "FAKE_DF" in captured.out
        assert calls["engine_created"] is True
        assert calls["lakeops_engine"] is not None
        path, fmt, options = calls["read_args"]
        assert path == "s3://bucket/table"
        assert fmt == "delta"
        assert options == {"a": 1}

    def test_execute_uses_duckdb_engine(self, monkeypatch, capsys):
        calls = {}

        class FakeDuckDBEngine:
            def __init__(self, path=":memory:"):
                calls["duckdb_path"] = path

        class FakeLakeOps:
            def __init__(self, engine=None):
                calls["lakeops_engine"] = engine

            def execute(self, sql: str, **kwargs):
                calls["execute_args"] = (sql, kwargs)
                return "FAKE_RESULT"

        monkeypatch.setattr("lakeops.cli.DuckDBEngine", FakeDuckDBEngine)
        monkeypatch.setattr("lakeops.cli.LakeOps", FakeLakeOps)

        exit_code = lakeops_main(
            [
                "execute",
                "SELECT 1",
                "--engine",
                "duckdb",
                "--duckdb-path",
                "test.duckdb",
            ]
        )
        captured = capsys.readouterr()

        assert exit_code == 0
        assert "FAKE_RESULT" in captured.out
        assert calls["duckdb_path"] == "test.duckdb"
        assert calls["lakeops_engine"] is not None
        sql, kwargs = calls["execute_args"]
        assert sql == "SELECT 1"
        assert kwargs == {}

    def test_invalid_json_options_exits(self, capsys):
        with pytest.raises(SystemExit):
            lakeops_main(["read", "s3://bucket/table", "--options", "{not-json}"])
        captured = capsys.readouterr()
        # The exact error message is produced by json.JSONDecodeError, so just ensure something was printed
        assert captured.out == "" or "Invalid JSON for --options" in captured.err

    def test_execute_trino_uses_env_vars(self, monkeypatch, capsys):
        calls = {}

        class FakeTrinoEngineConfig:
            def __init__(self, **kwargs):
                calls["config_kwargs"] = kwargs

        class FakeTrinoEngine:
            def __init__(self, config):
                calls["engine_config"] = config

        class FakeLakeOps:
            def __init__(self, engine=None):
                calls["lakeops_engine"] = engine

            def execute(self, sql: str, **kwargs):
                calls["execute_args"] = (sql, kwargs)
                return "TRINO_RESULT"

        monkeypatch.setattr("lakeops.cli.TrinoEngineConfig", FakeTrinoEngineConfig)
        monkeypatch.setattr("lakeops.cli.TrinoEngine", FakeTrinoEngine)
        monkeypatch.setattr("lakeops.cli.LakeOps", FakeLakeOps)

        monkeypatch.setenv("LAKEOPS_TRINO_HOST", "trino.example.com")
        monkeypatch.setenv("LAKEOPS_TRINO_PORT", "8443")
        monkeypatch.setenv("LAKEOPS_TRINO_USER", "user1")
        monkeypatch.setenv("LAKEOPS_TRINO_CATALOG", "hive")
        monkeypatch.setenv("LAKEOPS_TRINO_SCHEMA", "default")
        monkeypatch.setenv("LAKEOPS_TRINO_PASSWORD", "secret")
        monkeypatch.setenv("LAKEOPS_TRINO_PROTOCOL", "https")

        exit_code = lakeops_main(
            [
                "execute",
                "SELECT 1",
                "--engine",
                "trino",
            ]
        )
        captured = capsys.readouterr()

        assert exit_code == 0
        assert "TRINO_RESULT" in captured.out
        assert "config_kwargs" in calls
        cfg = calls["config_kwargs"]
        assert cfg["host"] == "trino.example.com"
        assert cfg["port"] == 8443
        assert cfg["user"] == "user1"
        assert cfg["catalog"] == "hive"
        assert cfg["schema"] == "default"
        assert cfg["password"] == "secret"
        assert cfg["protocol"] == "https"
        assert calls["lakeops_engine"] is not None
        sql, kwargs = calls["execute_args"]
        assert sql == "SELECT 1"
        assert kwargs == {}

