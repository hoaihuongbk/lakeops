## Working With the LakeOps CLI

LakeOps ships with a command‑line interface so you can run the same operations you use
in Python directly from the shell.

After installing:

```bash
pip install lakeops
```

you get a `lakeops` command on your `PATH`.

```bash
lakeops --help
```

prints the list of available commands and options.

---

## Commands overview

The CLI mirrors the main `LakeOps` APIs:

- `lakeops read` → `LakeOps.read`
- `lakeops execute` → `LakeOps.execute`

### `lakeops read`

`read` loads a dataset using the default Polars engine and prints the result:

```bash
lakeops read PATH [--format FORMAT] [--options JSON]
```

- **`PATH`**: storage path or table location (for example `s3://bucket/table` or `/tmp/table.delta`).
- **`--format`**: table format, default is `delta`. Supported values:
  - `delta`
  - `parquet`
  - `csv`
  - `json`
- **`--options`**: JSON‑encoded dict of engine options, passed through to `LakeOps.read`.

Examples:

```bash
# Read a Delta table from local storage
lakeops read /data/delta/customers --format delta

# Read a parquet dataset
lakeops read s3://lake/orders --format parquet

# Pass extra options as JSON
lakeops read /data/delta/customers \
  --format delta \
  --options '{"version": 5}'
```

Internally this is equivalent to:

```python
from lakeops import LakeOps
from lakeops.core.engines import PolarsEngine

ops = LakeOps(engine=PolarsEngine())
df = ops.read("/data/delta/customers", format="delta", options={"version": 5})
```

> Note: the CLI currently uses the Polars engine for `read`.

### `lakeops execute`

`execute` runs SQL using one of the SQL engines and prints the result:

```bash
lakeops execute SQL --engine {duckdb,trino} [ENGINE OPTIONS]
```

- **`SQL`**: the SQL query to run (wrap in quotes in the shell).
- **`--engine`**:
  - `duckdb` (default): in‑process DuckDB.
  - `trino`: remote Trino cluster.

#### DuckDB

When using DuckDB, you can choose between an in‑memory database or a file:

```bash
# In‑memory (default)
lakeops execute "SELECT 1" --engine duckdb

# File‑backed database
lakeops execute "SELECT * FROM my_table" \
  --engine duckdb \
  --duckdb-path /tmp/lakeops.duckdb
```

Internally this maps to:

```python
from lakeops import LakeOps
from lakeops.core.engines import DuckDBEngine

ops = LakeOps(engine=DuckDBEngine(path=":memory:"))
df = ops.execute("SELECT 1")
```

#### Trino

For Trino, you configure the connection via flags or environment variables.

Flags:

```bash
lakeops execute "SELECT * FROM my_table" \
  --engine trino \
  --trino-host trino.example.com \
  --trino-port 8443 \
  --trino-user my_user \
  --trino-catalog hive \
  --trino-schema default \
  --trino-password my_password \
  --trino-protocol https
```

Or with environment variables:

```bash
export LAKEOPS_TRINO_HOST=trino.example.com
export LAKEOPS_TRINO_PORT=8443
export LAKEOPS_TRINO_USER=my_user
export LAKEOPS_TRINO_CATALOG=hive
export LAKEOPS_TRINO_SCHEMA=default
export LAKEOPS_TRINO_PASSWORD=my_password
export LAKEOPS_TRINO_PROTOCOL=https

lakeops execute "SELECT * FROM my_table" --engine trino
```

This corresponds to:

```python
from lakeops import LakeOps
from lakeops.core.engines import TrinoEngine, TrinoEngineConfig

config = TrinoEngineConfig(
    host="trino.example.com",
    port=8443,
    user="my_user",
    catalog="hive",
    schema="default",
    password="my_password",
    protocol="https",
)
ops = LakeOps(engine=TrinoEngine(config))
df = ops.execute("SELECT * FROM my_table")
```

---

## Error handling

- **Invalid JSON in `--options`** causes the CLI to exit with a clear error message.
- **Missing Trino connection parameters** (host, user, catalog, schema) also cause an early exit
  with a list of missing fields.

You can always inspect the available options with:

```bash
lakeops --help
lakeops read --help
lakeops execute --help
```

