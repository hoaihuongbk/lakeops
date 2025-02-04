# LakeOps

A modern data lake operations toolkit supporting multiple formats (Delta, Iceberg, Parquet) and engines (Spark, Polars).

## Features

- Multi-format support: Delta, Iceberg, Parquet
- Multiple engine backends: Apache Spark, Polars (default)
- Storage operations: read, write

To learn more, read the [user guide](https://hoaihuongbk.github.io/lakeops/).

## Quick Start

### Installation
```bash
pip install lakeops
```

### Sample Usage

```python
from pyspark.sql import SparkSession
from lakeops import LakeOps
from lakeops.core.engine import SparkEngine

# Init Spark session and create LakeOps instance
spark = SparkSession.builder.getOrCreate()
engine = SparkEngine(spark)
ops = LakeOps(engine)

# Read data from table name
df = ops.read("s3://local/test/table", format="parquet")

# Write data to table name
ops.write(df, "s3://local/test/table", format="parquet")

```

