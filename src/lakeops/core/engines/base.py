from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class Engine(ABC):
    @abstractmethod
    def read(
        self, path: str, format: str = "delta", options: Optional[Dict[str, Any]] = None
    ) -> Any:
        pass

    @abstractmethod
    def write(
        self,
        data: Any,
        path: str,
        format: str = "delta",
        mode: str = "overwrite",
        options: Optional[Dict[str, Any]] = None,
    ) -> None:
        pass

    @abstractmethod
    def execute(self, sql: str, **kwargs) -> Any:
        pass

    def is_storage_path(self, path: str) -> bool:
        ## If path contains a slash, it's a storage path
        return "/" in path
