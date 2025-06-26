import os
from lakeops import LakeOps
from lakeops.core.engines import DatabricksSparkConnectEngine

PROFILE_NAME = os.environ.get("DATABRICKS_PROFILE", "DEFAULT")

def main():
    try:
        from databricks.connect import DatabricksSession
    except ImportError:
        print("Databricks Connect is not installed. Exiting.")
        return

    print(f"Using profile: {PROFILE_NAME}")
    engine = DatabricksSparkConnectEngine(profile_name=PROFILE_NAME)
    lake_ops = LakeOps(engine)

    # 1. Query the first 100 rows from samples.nyctaxi.trips
    print("Querying the first 100 rows from samples.nyctaxi.trips...")
    df = lake_ops.execute("SELECT * FROM samples.nyctaxi.trips LIMIT 100")
    df.show()

    # 2. Filter for trips with trip_distance > 3
    print("Filtering for trips with trip_distance > 3...")
    filtered_df = df.filter(df.trip_distance > 3)
    filtered_df.show()

    # 3. Write the filtered DataFrame to a new table
    temp_table = "workspace.default.test_trips"
    print(f"Writing filtered data to table {temp_table}...")
    filtered_df.write.mode("overwrite").saveAsTable(temp_table)

    # 4. Show the contents of the new table
    print(f"Reading from {temp_table}...")
    df_new = lake_ops.execute(f"SELECT * FROM {temp_table}")
    df_new.show()

    # 5. Drop the new table
    print(f"Dropping table {temp_table}...")
    lake_ops.execute(f"DROP TABLE IF EXISTS {temp_table}")
    print("Done.")

if __name__ == "__main__":
    main()
