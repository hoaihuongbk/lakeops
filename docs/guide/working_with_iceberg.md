# Working with Iceberg

Apache Iceberg is a high-performance format for huge analytic tables that provides ACID transactions, schema evolution, and efficient querying. Here's how to use lakeops with Iceberg format.

## Setup
```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder.config(
        "spark.sql.extensions",
        "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
    )
    .config(
        "spark.sql.catalog.spark_catalog",
        "org.apache.iceberg.spark.SparkSessionCatalog",
    )
    .config("spark.sql.catalog.spark_catalog.type", "hive")
    .config("spark.sql.catalog.local", "org.apache.iceberg.spark.SparkCatalog")
    .config("spark.sql.catalog.local.type", "hadoop")
    .config("spark.sql.catalog.local.warehouse", "/app/data")
    .config("spark.sql.defaultCatalog", "local")
    .getOrCreate()
)

engine = SparkEngine(spark)
ops = LakeOps(engine)
```

## Reading Iceberg Tables

```python
# Read from path
df = ops.read("s3://path/to/table", format="iceberg")
    
# Read from table name
df = ops.read("local.db.table_name", format="iceberg")
# Show table
df.show(truncate=False)
```

## Writing Iceberg Tables

At this time, only writing to table name is supported

```python
# Write to table name
ops.write(df, "local.db.table_name", format="iceberg")
```
