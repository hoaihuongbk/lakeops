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

### Hashicorp Vault Backend
Integration with Hashicorp Vault KV v2 engine using the [hvac](https://hvac.readthedocs.io/) library.

#### Configuration via Environment Variables

In most production environments (for example, Kubernetes pods), Vault credentials are injected as environment variables.  
`VaultSecretManager` can auto-configure itself from the following variables, so you do not need to pass them explicitly:

- **Token authentication**
  - `LAKEOPS_VAULT_TOKEN` (preferred)
  - `VAULT_TOKEN` (fallback)

- **JWT/OIDC authentication**
  - `LAKEOPS_VAULT_ROLE` – Vault role name
  - `LAKEOPS_VAULT_JWT_TOKEN` – JWT/OIDC token value
  - `LAKEOPS_VAULT_JWT_PATH` – auth mount path (defaults to `jwt` if not set)

- **Kubernetes authentication**
  - `LAKEOPS_VAULT_ROLE` – Vault role name
  - `LAKEOPS_VAULT_K8S_AUTH_PATH` – auth mount path (defaults to `kubernetes`)
  - `LAKEOPS_VAULT_K8S_JWT_PATH` – path to the service account JWT file  
    (defaults to `/var/run/secrets/kubernetes.io/serviceaccount/token`)

Examples:

```bash
export LAKEOPS_VAULT_TOKEN="your-vault-token"
python your_app.py
```

```bash
export LAKEOPS_VAULT_ROLE="your-vault-role"
export LAKEOPS_VAULT_JWT_TOKEN="your-jwt-token"
export LAKEOPS_VAULT_JWT_PATH="jwt"
python your_app.py
```

```bash
export LAKEOPS_VAULT_ROLE="your-k8s-vault-role"
export LAKEOPS_VAULT_K8S_AUTH_PATH="kubernetes"
export LAKEOPS_VAULT_K8S_JWT_PATH="/var/run/secrets/kubernetes.io/serviceaccount/token"
python your_app.py
```

With these environment variables set, you can use minimal constructors like:

```python
from lakeops.core.secrets import VaultSecretManager

manager = VaultSecretManager(url="https://vault.example.com:8200")  # token auth from env
manager_jwt = VaultSecretManager(url="https://vault.example.com:8200", auth_method="jwt")
manager_k8s = VaultSecretManager(url="https://vault.example.com:8200", auth_method="kubernetes")
```

#### Token Authentication (Default)
```python
from lakeops.core.secrets import VaultSecretManager

manager = VaultSecretManager(
    url="https://vault.example.com:8200",
    token="your-vault-token"
)
```

#### JWT/OIDC Authentication
```python
manager = VaultSecretManager(
    url="https://vault.example.com:8200",
    auth_method="jwt",
    role="your-vault-role",
    jwt_token="your-jwt-token"
)
```

#### Kubernetes Authentication
This method automatically reads the service account token from the default Kubernetes path.
```python
manager = VaultSecretManager(
    url="https://vault.example.com:8200",
    auth_method="kubernetes",
    role="your-k8s-vault-role"
)
```

#### Operations
```python
# Write a secret (uses path: {scope}/{key} or just {key})
manager.write("api_key", "super-secret-value", scope="my-project")

# Read a secret (returns redacted by default)
value = manager.read("api_key", scope="my-project", redacted=True)
# Returns: *************alue
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
