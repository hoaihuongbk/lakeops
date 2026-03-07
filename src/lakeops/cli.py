from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict, Optional

from . import LakeOps
from .core.engines import DuckDBEngine, PolarsEngine, TrinoEngine, TrinoEngineConfig


def _parse_json_options(raw: Optional[str]) -> Optional[Dict[str, Any]]:
    if not raw:
        return None
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as e:
        raise SystemExit(f"Invalid JSON for --options: {e}") from e
    if not isinstance(value, dict):
        raise SystemExit("--options must be a JSON object (e.g. '{\"key\": \"value\"}')")
    return value


def _make_engine_for_read(args: argparse.Namespace) -> PolarsEngine:
    # For now, only Polars is supported for the read command.
    if args.engine == "polars":
        return PolarsEngine()
    raise SystemExit(f"Unsupported engine for read: {args.engine}")


def _make_engine_for_execute(args: argparse.Namespace):
    if args.engine == "duckdb":
        return DuckDBEngine(path=args.duckdb_path)

    if args.engine == "trino":
        host = args.trino_host or os.environ.get("LAKEOPS_TRINO_HOST")
        port_str = (
            str(args.trino_port)
            if args.trino_port is not None
            else os.environ.get("LAKEOPS_TRINO_PORT", "443")
        )
        user = args.trino_user or os.environ.get("LAKEOPS_TRINO_USER")
        catalog = args.trino_catalog or os.environ.get("LAKEOPS_TRINO_CATALOG")
        schema = args.trino_schema or os.environ.get("LAKEOPS_TRINO_SCHEMA")
        password = args.trino_password or os.environ.get("LAKEOPS_TRINO_PASSWORD")
        protocol = args.trino_protocol or os.environ.get("LAKEOPS_TRINO_PROTOCOL", "https")

        try:
            port = int(port_str)
        except ValueError as e:
            raise SystemExit(f"Invalid Trino port: {port_str}") from e

        missing = [
            name
            for name, val in {
                "host": host,
                "user": user,
                "catalog": catalog,
                "schema": schema,
            }.items()
            if not val
        ]
        if missing:
            raise SystemExit(
                "Missing Trino connection values: "
                + ", ".join(missing)
                + " (set flags or LAKEOPS_TRINO_* environment variables)"
            )

        config = TrinoEngineConfig(
            host=host,
            port=port,
            user=user,
            catalog=catalog,
            schema=schema,
            password=password,
            protocol=protocol,
        )
        return TrinoEngine(config)

    raise SystemExit(f"Unsupported engine for execute: {args.engine}")


def cmd_read(args: argparse.Namespace) -> None:
    engine = _make_engine_for_read(args)
    lo = LakeOps(engine=engine)
    df = lo.read(args.path, format=args.format, options=_parse_json_options(args.options))
    print(df)


def cmd_execute(args: argparse.Namespace) -> None:
    engine = _make_engine_for_execute(args)
    lo = LakeOps(engine=engine)
    result = lo.execute(args.sql)
    print(result)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lakeops",
        description="LakeOps command-line interface",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # read command
    p_read = subparsers.add_parser("read", help="Read a dataset and print it")
    p_read.add_argument("path", help="Storage path or schema/table name to read from")
    p_read.add_argument(
        "--format",
        default="delta",
        help="Table format (default: delta)",
    )
    p_read.add_argument(
        "--options",
        help="JSON-encoded dict of options passed to the underlying engine",
    )
    p_read.add_argument(
        "--engine",
        default="polars",
        choices=["polars"],
        help="Execution engine to use for read (currently only polars is supported)",
    )
    p_read.set_defaults(func=cmd_read)

    # execute command
    p_exec = subparsers.add_parser("execute", help="Execute a SQL query and print the result")
    p_exec.add_argument("sql", help="SQL query to execute")
    p_exec.add_argument(
        "--engine",
        default="duckdb",
        choices=["duckdb", "trino"],
        help="Execution engine to use for SQL (default: duckdb)",
    )
    p_exec.add_argument(
        "--duckdb-path",
        default=":memory:",
        help="DuckDB database path (default: :memory:)",
    )
    p_exec.add_argument("--trino-host", help="Trino host (or set LAKEOPS_TRINO_HOST)")
    p_exec.add_argument(
        "--trino-port",
        type=int,
        help="Trino port (or set LAKEOPS_TRINO_PORT, default: 443)",
    )
    p_exec.add_argument("--trino-user", help="Trino user (or set LAKEOPS_TRINO_USER)")
    p_exec.add_argument(
        "--trino-catalog",
        help="Trino catalog (or set LAKEOPS_TRINO_CATALOG)",
    )
    p_exec.add_argument(
        "--trino-schema",
        help="Trino schema (or set LAKEOPS_TRINO_SCHEMA)",
    )
    p_exec.add_argument(
        "--trino-password",
        help="Trino password (or set LAKEOPS_TRINO_PASSWORD)",
    )
    p_exec.add_argument(
        "--trino-protocol",
        choices=["http", "https"],
        help="Trino protocol (or set LAKEOPS_TRINO_PROTOCOL, default: https)",
    )
    p_exec.set_defaults(func=cmd_execute)

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

