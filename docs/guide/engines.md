# Engines

LakeOps supports multiple execution engines:

## Polars Engine
Default engine optimized for single-node operations:
```python
ops = LakeOps()  # Uses PolarsEngine by default
```

## Spark Engine
For distributed processing:

```python
from lakeops.core.engines import SparkEngine
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()
ops = LakeOps(SparkEngine(spark))

```