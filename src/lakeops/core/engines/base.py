from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class Engine(ABC):
    @abstractmethod
    def read_table(
        self, path: str, format: str, options: Optional[Dict[str, Any]] = None
    ) -> Any:
        pass

    @abstractmethod
    def write_table(
        self,
        data: Any,
        path: str,
        format: str,
        mode: str = "overwrite",
        options: Optional[Dict[str, Any]] = None,
    ) -> None:
        pass
