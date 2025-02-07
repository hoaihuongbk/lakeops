from typing import Optional, Dict, Any
from sqlalchemy import create_engine
import polars as pl
from trino.auth import BasicAuthentication

from .base import Engine

from dataclasses import dataclass
from typing import Optional


@dataclass
class TrinoEngineConfig:
    host: str
    port: int
    user: str
    catalog: str
    schema: str
    password: Optional[str] = None

    @property
    def connection(self):
        # https://sfu-db.github.io/connector-x/databases/trino.html
        # https://github.com/trinodb/trino-python-client

        auth = None
        if self.password:
            auth = BasicAuthentication(self.user, self.password)

        return create_engine(
            f"trino://{self.user}@{self.host}:{self.port}/{self.catalog}/{self.schema}",
            connect_args={
                "auth": auth,
                "http_scheme": "https",
            },
        )


class TrinoEngine(Engine):
    def __init__(self, config: TrinoEngineConfig):
        self.connection = config.connection.connect()

    def read_table(
        self, path: str, format: str, options: Optional[Dict[str, Any]] = None
    ) -> Any:
        raise NotImplementedError("TrinoEngine does not support read_table")

    def write_table(
        self,
        data: Any,
        path: str,
        format: str,
        mode: str = "overwrite",
        options: Optional[Dict[str, Any]] = None,
    ) -> None:
        raise NotImplementedError("TrinoEngine does not support write_table")

    def execute(self, sql: str, **kwargs) -> Any:
        return pl.read_database(query=sql, connection=self.connection, **kwargs)
