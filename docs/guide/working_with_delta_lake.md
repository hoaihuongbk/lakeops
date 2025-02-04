# Working with Delta Lake

Delta Lake provides ACID transactions, scalable metadata handling, and unifies streaming and batch data processing.
Here's how to use lakeops with Delta Lake format.

## Setup

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder.config(
        "spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension"
    )
    .config(
        "spark.sql.catalog.spark_catalog",
        "org.apache.spark.sql.delta.catalog.DeltaCatalog",
    )
    .getOrCreate()
)

engine = SparkEngine(spark)
ops = LakeOps(engine)
```

## Reading Delta Tables

```python

# Read from path
df = ops.read("s3://path/to/table", format="delta")

# Read from table name
df = ops.read("table_name", format="delta")

# Show table
df.show(truncate=False)

```

## Writing Delta Tables

```python

# Write to path
ops.write(df, "s3://path/to/table", format="delta")

# Write to table name
ops.write(df, "table_name", format="delta")

```