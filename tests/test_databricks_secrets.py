import pytest
import logging
from unittest.mock import MagicMock
from databricks.sdk import WorkspaceClient
from lakeops.core.secrets import DatabricksSecretManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
def mock_workspace_client():
    mock_client = MagicMock(spec=WorkspaceClient)
    mock_secrets = MagicMock()

    # Set up the secrets attribute and its methods
    mock_client.secrets = mock_secrets

    # Mock for read operation
    secret_response = MagicMock()
    secret_response.value = "test_read_value"
    mock_secrets.get_secret.return_value = secret_response

    # Mock for write operation
    mock_secrets.put_secret.return_value = None
    mock_secrets.create_scope.return_value = None

    return mock_client


@pytest.fixture
def databricks_secret_manager(mock_workspace_client):
    return DatabricksSecretManager(workspace_client=mock_workspace_client)


def test_write_and_read_secret(mock_workspace_client, databricks_secret_manager):
    logger.info("Testing Databricks write and read secret")
    # Write secret
    databricks_secret_manager.write("test_key", "test_value", scope="test_scope")

    # Verify write calls
    mock_workspace_client.secrets.put_secret.assert_called_once_with(
        scope="test_scope", key="test_key", string_value="test_value"
    )

    # Read and verify value
    value = databricks_secret_manager.read(
        "test_read_key", scope="test_scope", show_redacted=False
    )
    # Verify read calls
    mock_workspace_client.secrets.get_secret.assert_called_once_with(
        scope="test_scope", key="test_read_key"
    )

    logger.info(f"Read secret value: {value}")
    assert value == "test_read_value"
