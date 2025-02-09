from dataclasses import dataclass
from typing import Any, Dict, Optional

import polars as pl

from .base import Engine


@dataclass
class TrinoEngineConfig:
    host: str
    port: int
    user: str
    catalog: str
    schema: str
    password: Optional[str] = None
    protocol: str = "https"

    @property
    def connection(self):
        # https://sfu-db.github.io/connector-x/databases/trino.html
        # https://github.com/trinodb/trino-python-client
        from sqlalchemy import create_engine
        from trino.auth import BasicAuthentication

        auth = None
        if self.password:
            auth = BasicAuthentication(self.user, self.password)

        return create_engine(
            f"trino://{self.user}@{self.host}:{self.port}/{self.catalog}/{self.schema}",
            connect_args={
                "auth": auth,
                "http_scheme": self.protocol,
            },
        )


class TrinoEngine(Engine):
    def __init__(self, config: TrinoEngineConfig):
        self.connection = config.connection.connect()

    def read(
        self, path: str, format: str = "delta", options: Optional[Dict[str, Any]] = None
    ) -> Any:
        raise NotImplementedError("TrinoEngine does not support read_table")

    def write(
        self,
        data: Any,
        path: str,
        format: str = "delta",
        mode: str = "overwrite",
        options: Optional[Dict[str, Any]] = None,
    ) -> None:
        raise NotImplementedError("TrinoEngine does not support write_table")

    def is_select_query(self, sql: str) -> bool:
        # Remove leading/trailing whitespace and get first word
        first_word = sql.strip().split()[0].upper()
        return first_word == "SELECT"

    def execute(self, sql: str, **kwargs) -> Any:
        if not self.is_select_query(sql):
            raise ValueError("TrinoEngine only supports SELECT queries")
        return pl.read_database(query=sql, connection=self.connection, **kwargs)
