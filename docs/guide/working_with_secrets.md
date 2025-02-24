# Working with Secrets

LakeOps provides a flexible secrets management system that supports multiple backend implementations.

## Quick Start

```python
from lakeops.core.secrets import SQLiteSecretManager
# Using SQLite backend (local development)
secret_manager = SQLiteSecretManager()
secret_manager.write("api_key", "my-secret-value")
value = secret_manager.read("api_key")  # Returns: ********value
```

## Available Backends

### SQLite Backend
Perfect for local development and testing. Stores secrets in a local SQLite database.
```python
from lakeops.core.secrets import SQLiteSecretManager
manager = SQLiteSecretManager("secrets.db")
manager.write("key", "value")
manager.read("key", show_redacted=True)  # Returns redacted value
manager.read("key", show_redacted=False)  # Returns full value
```

### Databricks Backend
Integration with Databricks Secrets API using the official [databricks-sdk](https://pypi.org/project/databricks-sdk/) package.
For details on authentication, refer to the [official documentation](https://docs.databricks.com/dev-tools/sdk/python/latest/authentication.html).

```python
from lakeops.core.secrets import DatabricksSecretManager

manager = DatabricksSecretManager()
manager.write("key", "value", scope="my-scope")
manager.read("key", scope="my-scope")
```


## Best Practices
1. Always use scopes in production environments
2. Use redacted values when logging
3. Rotate secrets periodically
4. Use environment-specific scopes (dev, staging, prod)

## Security Notes
- Secrets are automatically redacted when read (show last 4 characters)
- SQLite backend stores secrets locally - use only for development
- Databricks backend leverages enterprise-grade security
