import pytest
from unittest.mock import MagicMock, patch, mock_open
from lakeops.core.secrets import VaultSecretManager
import hvac

pytestmark = pytest.mark.vault


@pytest.fixture
def mock_vault_client():
    with patch("hvac.Client") as mock:
        yield mock


def test_vault_init_token(mock_vault_client):
    VaultSecretManager(url="http://localhost:8200", token="test-token")
    mock_vault_client.return_value.token = "test-token"
    # The client is initialized without token in __init__ if it's not 'token' method
    # but for token method it's set after.


def test_vault_init_jwt(mock_vault_client):
    mock_client = mock_vault_client.return_value
    VaultSecretManager(
        url="http://localhost:8200",
        auth_method="jwt",
        role="test-role",
        jwt_token="test-jwt",
    )
    mock_client.auth.jwt.login.assert_called_once_with(
        role="test-role", jwt="test-jwt", path="jwt"
    )


def test_vault_init_kubernetes(mock_vault_client):
    mock_client = mock_vault_client.return_value
    with patch("builtins.open", mock_open(read_data="test-k8s-jwt")):
        VaultSecretManager(
            url="http://localhost:8200", auth_method="kubernetes", role="test-role"
        )
    mock_client.auth.kubernetes.login.assert_called_once_with(
        role="test-role", jwt="test-k8s-jwt", mount_point="kubernetes"
    )


def test_vault_write(mock_vault_client):
    manager = VaultSecretManager(url="http://localhost:8200", token="test-token")

    manager.write("test_key", "test_value")

    manager.client.secrets.kv.v2.create_or_update_secret.assert_called_once_with(
        path="test_key",
        secret={"test_key": "test_value"},
        mount_point="secret",
    )


def test_vault_write_with_scope(mock_vault_client):
    manager = VaultSecretManager(url="http://localhost:8200", token="test-token")

    manager.write("test_key", "test_value", scope="test_scope")

    manager.client.secrets.kv.v2.create_or_update_secret.assert_called_once_with(
        path="test_scope/test_key",
        secret={"test_key": "test_value"},
        mount_point="secret",
    )


def test_vault_read(mock_vault_client):
    manager = VaultSecretManager(url="http://localhost:8200", token="test-token")

    # Mock response from hvac
    mock_response = {"data": {"data": {"test_key": "test_value"}}}
    manager.client.secrets.kv.v2.read_secret_version.return_value = mock_response

    value = manager.read("test_key", redacted=False)

    assert value == "test_value"
    manager.client.secrets.kv.v2.read_secret_version.assert_called_once_with(
        path="test_key",
        mount_point="secret",
    )


def test_vault_read_redacted(mock_vault_client):
    manager = VaultSecretManager(url="http://localhost:8200", token="test-token")

    mock_response = {"data": {"data": {"api_key": "abcd1234efgh5678"}}}
    manager.client.secrets.kv.v2.read_secret_version.return_value = mock_response

    value = manager.read("api_key", redacted=True)
    assert value == "************5678"


def test_vault_read_nonexistent_path(mock_vault_client):
    manager = VaultSecretManager(url="http://localhost:8200", token="test-token")

    manager.client.secrets.kv.v2.read_secret_version.side_effect = hvac.exceptions.InvalidPath

    with pytest.raises(KeyError, match="Secret path not found"):
        manager.read("nonexistent_key")


def test_vault_read_nonexistent_key(mock_vault_client):
    manager = VaultSecretManager(url="http://localhost:8200", token="test-token")

    # Path exists but key doesn't (different from original key)
    mock_response = {"data": {"data": {"different_key": "test_value"}}}
    manager.client.secrets.kv.v2.read_secret_version.return_value = mock_response

    with pytest.raises(KeyError, match="Key 'test_key' not found"):
        manager.read("test_key")
