# Basic Usage

```python
from lakeops import LakeOps
from lakeops.core.engines import SparkEngine

# Use default Polars engine
ops = LakeOps()

# Or use Spark engine
spark_ops = LakeOps(SparkEngine(spark))

# Read/Write operations
df = ops.read("table_path", format="delta")
ops.write(df, "new_path", format="iceberg")

```