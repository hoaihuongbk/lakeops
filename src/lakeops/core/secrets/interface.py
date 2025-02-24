from abc import ABC, abstractmethod
from typing import Optional


class SecretManager(ABC):
    @abstractmethod
    def write(self, key: str, value: str, scope: Optional[str] = None) -> None:
        """Write a secret value for the given key and optional scope"""
        pass

    @abstractmethod
    def read(
        self, key: str, scope: Optional[str] = None, show_redacted: bool = True
    ) -> str:
        """Read a secret value for the given key and optional scope"""
        pass
