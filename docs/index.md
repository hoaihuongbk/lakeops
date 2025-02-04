# LakeOps

A modern data lake operations toolkit supporting multiple formats (Delta, Iceberg, Parquet) and engines (Spark, Polars).

## Features
- Multi-format support: Delta, Iceberg, Parquet
- Multiple engine backends: Apache Spark, Polars
- Standardized DataFrame interface using Polars/Arrow
- Simple and intuitive API

## Installation
```bash
pip install lakeops
```

## Quick Example
```python
from lakeops import LakeOps

# Initialize with default Polars engine
ops = LakeOps()

# Read Delta table
df = ops.read("path/to/table", format="delta")

# Write as Iceberg
ops.write(df, "path/to/new/table", format="iceberg")
```