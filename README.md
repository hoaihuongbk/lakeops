# LakeOps

A modern data lake operations toolkit supporting multiple formats (Delta, Iceberg, Parquet) and engines (Spark, Polars).

## Features

- Multi-format support: Delta, Iceberg, Parquet
- Multiple engine backends: Apache Spark, Polars (default)
- Storage operations: read, write

## Quick Start

```python
from pyspark.sql import SparkSession
from lakeops import LakeOps
from lakeops.core.engine import SparkEngine, PolarsEngine

# Set either engine Spark or Polars
spark = SparkSession.builder
    .appName("LakeOps")
    .config("spark.jars.packages", "iceberg-spark-runtime-3.5_2.12:1.6.1")
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
    .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkSessionCatalog") \
    .config("spark.sql.catalog.local", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.local.type", "hadoop") \
    .config("spark.sql.catalog.local.warehouse", "/app/data") \
    .getOrCreate()

engine = SparkEngine(spark)
# engine = PolarsEngine()

# Init lakeops
ops = LakeOps(engine)

# Read data from table name
df = ops.read("local.db.test_table", format="iceberg")

# Write data to table name
ops.write(df, "local.db.test_table", format="iceberg")

```

## Installation
```bash
pip install lakeops
```
