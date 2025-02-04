---
hide:
  - navigation
---

# Engines

LakeOps supports multiple execution engines:

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