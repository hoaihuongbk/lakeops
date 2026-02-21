from typing import Any, Dict, Optional
import hvac
from .interface import SecretManager
from .utils import redact_secret


class VaultSecretManager(SecretManager):
    """
    Hashicorp Vault implementation of SecretManager using hvac library.
    Supports KV v2 engine.
    """

    def __init__(
        self,
        url: str,
        token: Optional[str] = None,
        mount_point: str = "secret",
        **kwargs: Any,
    ):
        """
        Initialize VaultSecretManager.

        Args:
            url: The Vault server URL
            token: Vault token for authentication
            mount_point: The mount point of the KV engine (default: 'secret')
            **kwargs: Additional arguments passed to hvac.Client
        """
        self.client = hvac.Client(url=url, token=token, **kwargs)
        self.mount_point = mount_point

    def write(self, key: str, value: str, scope: Optional[str] = None) -> None:
        """
        Write a secret to Vault KV v2.
        If scope is provided, it's used as part of the path: {scope}/{key}

        Args:
            key: Secret key
            value: Secret value
            scope: Optional scope/path prefix
        """
        path = f"{scope}/{key}" if scope else key
        
        # In KV v2, we write a dictionary
        self.client.secrets.kv.v2.create_or_update_secret(
            path=path,
            secret={key: value},
            mount_point=self.mount_point,
        )

    def read(
        self, key: str, scope: Optional[str] = None, redacted: bool = True
    ) -> str:
        """
        Read a secret from Vault KV v2.

        Args:
            key: Secret key
            scope: Optional scope/path prefix
            redacted: Whether to redact the output

        Returns:
            The secret value
        """
        path = f"{scope}/{key}" if scope else key
        
        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point=self.mount_point,
            )
            # The value is stored in the dictionary with the same key
            value = response["data"]["data"][key]
            return redact_secret(value) if redacted else value
        except hvac.exceptions.InvalidPath:
            raise KeyError(f"Secret path not found: {path}")
        except KeyError:
            raise KeyError(f"Key '{key}' not found in secret at path: {path}")
