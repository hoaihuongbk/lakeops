---
hide:
  - navigation
---

# LakeOps

A modern data lake operations toolkit working with multiple table formats (Delta, Iceberg, Parquet) and engines 
(Spark, Polars) via the same APIs.

## Features
- Multi-format support: Delta, Iceberg, Parquet, JSON, CSV
- Multiple engine backends: Polars, Apache Spark, Trino, Google Sheets
- Storage operations: read, write, execute SQL query
- Secrets management: local (SQLLite), Databricks

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
ops.write(df, "local.db.table", format="iceberg")
```