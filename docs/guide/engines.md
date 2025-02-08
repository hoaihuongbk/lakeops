---
hide:
  - navigation
---

# Engines

LakeOps supports multiple execution engines:

```bash
# Default
pip install lakeops

# Install pyspark engine
pip install lakeops[spark]

# Install trino engine
pip install lakeops[trino]

# Install Google Sheets engine
pip install lakeops[gsheet]

# Install spark, trino, gsheet engines
pip install lakeops[spark,trino,gsheet]
```


## Polars Engine
Default engine optimized for single-node operations, working with `polars.DataFrame`.
```python
ops = LakeOps()  # Uses PolarsEngine by default
```

## Spark Engine
For distributed processing and working with `pyspark.sql.DataFrame`:

```python
from lakeops.core.engines import SparkEngine
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()
engine = SparkEngine(spark)
ops = LakeOps(engine)

```

## Trino Engine

```python
from lakeops.core.engines import TrinoEngine, TrinoEngineConfig

trino_config = TrinoEngineConfig(
    host="localhost",
    port=8080,
    user="test_user",
    catalog="test_catalog",
    schema="test_schema",
    password="test_password",
)
engine = TrinoEngine(trino_config)
ops = LakeOps(engine)

```

## Google Sheets Engine

```python
from lakeops.core.engines import GoogleSheetsEngine

credentials = {
    "type": "service_account",
    "project_id": "api-project-XXX",
    "private_key_id": "2cd … ba4",
    "private_key": "-----BEGIN PRIVATE KEY-----\nNrDyLw … jINQh/9\n-----END PRIVATE KEY-----\n",
    "client_email": "473000000000-yoursisdifferent@developer.gserviceaccount.com",
    "client_id": "473 … hd.apps.googleusercontent.com",
    ...
}

engine = GoogleSheetsEngine(credentials)
ops = LakeOps(engine)

```