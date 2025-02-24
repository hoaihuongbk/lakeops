from .interface import SecretManager
from databricks.sdk import WorkspaceClient
from .utils import redact_secret
from typing import Optional


class DatabricksSecretManager(SecretManager):
    def __init__(self, workspace_client: Optional[WorkspaceClient] = None):
        self.client = workspace_client or WorkspaceClient()
        self.secrets = self.client.secrets

    def write(self, key: str, value: str, scope: Optional[str] = None) -> None:
        if not scope:
            raise ValueError("Scope is required for Databricks secrets")

        # Create scope if it doesn't exist
        try:
            self.secrets.create_scope(scope=scope)
        except Exception:
            # Scope already exists
            pass

        self.secrets.put_secret(scope=scope, key=key, string_value=value)

    def read(
        self, key: str, scope: Optional[str] = None, redacted: bool = True
    ) -> str:
        if not scope:
            raise ValueError("Scope is required for Databricks secrets")

        value = self.secrets.get_secret(scope=scope, key=key).value
        return redact_secret(value) if redacted else value
