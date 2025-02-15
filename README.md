# LakeOps

[![PyPI version](https://badge.fury.io/py/lakeops.svg)](https://badge.fury.io/py/lakeops)
[![Python Versions](https://img.shields.io/pypi/pyversions/lakeops.svg)](https://pypi.org/project/lakeops/)
[![Tests](https://github.com/hoaihuongbk/lakeops/actions/workflows/test.yml/badge.svg)](https://github.com/hoaihuongbk/lakeops/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/hoaihuongbk/lakeops/branch/main/graph/badge.svg)](https://codecov.io/gh/hoaihuongbk/lakeops)


A modern data lake operations toolkit working with multiple table formats (Delta, Iceberg, Parquet) and engines
(Spark, Polars) via the same APIs.

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
