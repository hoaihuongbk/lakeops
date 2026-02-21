from typing import Any, Dict, Optional
import hvac
from .interface import SecretManager
from .utils import redact_secret


class VaultSecretManager(SecretManager):
    """
    Hashicorp Vault implementation of SecretManager using hvac library.
    Supports KV v2 engine and multiple authentication methods:
    - Token (default)
    - JWT/OIDC
    - Kubernetes
    """

    def __init__(
        self,
        url: str,
        token: Optional[str] = None,
        auth_method: str = "token",
        mount_point: str = "secret",
        **kwargs: Any,
    ):
        """
        Initialize VaultSecretManager.

        Args:
            url: The Vault server URL
            token: Vault token for authentication (if auth_method is 'token')
            auth_method: Authentication method ('token', 'jwt', 'kubernetes')
            mount_point: The mount point of the KV engine (default: 'secret')
            **kwargs: Additional arguments:
                - For 'jwt': jwt_token (str), role (str), path (str, default 'jwt')
                - For 'kubernetes': role (str), jwt_path (str, default '/var/run/secrets/kubernetes.io/serviceaccount/token'), path (str, default 'kubernetes')
                - Other arguments passed to hvac.Client
        """
        self.client = hvac.Client(url=url, **kwargs)
        self.mount_point = mount_point
        self.auth_method = auth_method.lower()

        if self.auth_method == "token":
            if token:
                self.client.token = token
        elif self.auth_method == "jwt":
            self._authenticate_jwt(**kwargs)
        elif self.auth_method == "kubernetes":
            self._authenticate_kubernetes(**kwargs)
        else:
            raise ValueError(f"Unsupported authentication method: {auth_method}")

    def _authenticate_jwt(self, **kwargs):
        """Authenticate using JWT method."""
        role = kwargs.get("role")
        jwt_token = kwargs.get("jwt_token")
        path = kwargs.get("path", "jwt")

        if not role or not jwt_token:
            raise ValueError("Role and jwt_token are required for JWT authentication")

        self.client.auth.jwt.login(role=role, jwt=jwt_token, path=path)

    def _authenticate_kubernetes(self, **kwargs):
        """Authenticate using Kubernetes method."""
        role = kwargs.get("role")
        path = kwargs.get("path", "kubernetes")
        jwt_path = kwargs.get(
            "jwt_path", "/var/run/secrets/kubernetes.io/serviceaccount/token"
        )

        if not role:
            raise ValueError("Role is required for Kubernetes authentication")

        with open(jwt_path, "r") as f:
            jwt = f.read().strip()

        self.client.auth.kubernetes.login(role=role, jwt=jwt, mount_point=path)

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

    def read(self, key: str, scope: Optional[str] = None, redacted: bool = True) -> str:
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
