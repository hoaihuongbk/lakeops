from abc import ABC, abstractmethod
from typing import Optional


class SecretManager(ABC):
    @abstractmethod
    def write(
        self, key: str, value: str, scope: Optional[str] = None
    ) -> None:
        """Write a secret value for the given key and optional scope

        Args:
            key: The key name of the secret to write
            value: The secret value to write
            scope: Optional scope/namespace for the secret

        Returns:
            None
        """

        pass
    @abstractmethod
    def read(
        self, key: str, scope: Optional[str] = None, redacted: bool = True
    ) -> str:
        """Read a secret value for the given key and optional scope

        Args:
            key: The key name of the secret to read
            scope: Optional scope/namespace for the secret
            redacted: Whether to redact value instead of actual secret

        Returns:
            string: The secret value or redacted version if redacted is True
        """

        pass