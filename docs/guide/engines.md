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

# Install spark and trino
pip install lakeops[spark,trino]
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