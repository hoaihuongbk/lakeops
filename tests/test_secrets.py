import pytest
import logging
from lakeops.core.secrets import SQLiteSecretManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
def secret_manager(tmp_path):
    logger.info(f"Using temporary directory: {tmp_path}")
    db_path = tmp_path / "test_secrets.db"
    return SQLiteSecretManager(str(db_path))


def test_write_and_read_secret(secret_manager):
    logger.info("Testing write and read secret")
    secret_manager.write("test_key", "test_secret_value")
    value = secret_manager.read("test_key", redacted=False)
    assert value == "test_secret_value"


def test_read_redacted_secret(secret_manager):
    logger.info("Testing read redacted secret")
    secret_manager.write("api_key", "abcd1234efgh5678")
    redacted_value = secret_manager.read("api_key")
    assert redacted_value == "************5678"


def test_nonexistent_secret(secret_manager):
    logger.info("Testing nonexistent secret read")
    with pytest.raises(KeyError):
        secret_manager.read("nonexistent_key")


def test_update_existing_secret(secret_manager):
    logger.info("Testing secret update")
    secret_manager.write("update_key", "initial_value")
    secret_manager.write("update_key", "updated_value")
    value = secret_manager.read("update_key", redacted=False)
    assert value == "updated_value"
