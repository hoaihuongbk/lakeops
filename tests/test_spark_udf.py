import pytest
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf

pytestmark = pytest.mark.spark

from pyspark.sql.types import BooleanType, DoubleType, StringType, ArrayType, StructType, StructField
from lakeops.udf import (
    point_in_polygon,
    calculate_distance,
    json_extract,
    is_valid_json,
    encode_geohash,
    decode_geohash,
)



def register_udfs(spark):
    # Create PySpark UDFs
    point_in_polygon_udf = udf(point_in_polygon, BooleanType())
    calculate_distance_udf = udf(calculate_distance, DoubleType())
    json_extract_udf = udf(json_extract, StringType())
    is_valid_json_udf = udf(is_valid_json, BooleanType())
    encode_geohash_udf = udf(encode_geohash, StringType())

    location_type = StructType([
        StructField("lat", DoubleType(), False),
        StructField("lon", DoubleType(), False)
    ])
    decode_geohash_udf = udf(lambda x: list(decode_geohash(x)), location_type)

    # Register with Spark
    spark.udf.register("point_in_polygon", point_in_polygon_udf)
    spark.udf.register("calculate_distance", calculate_distance_udf)
    spark.udf.register("json_extract", json_extract_udf)
    spark.udf.register("is_valid_json", is_valid_json_udf)
    spark.udf.register("encode_geohash", encode_geohash_udf)
    spark.udf.register("decode_geohash", decode_geohash_udf)




@pytest.fixture
def test_data(spark):
    register_udfs(spark)
    data = [
        (
            '{"type":"Point","coordinates":[0.5,0.5]}',
            '{"type":"Polygon","coordinates":[[[0,0],[1,0],[1,1],[0,1],[0,0]]]}',
            '{"name": "Store A", "details": {"category": "retail", "id": 123}}',
        ),
        (
            '{"type":"Point","coordinates":[2.0,2.0]}',
            '{"type":"Polygon","coordinates":[[[0,0],[1,0],[1,1],[0,1],[0,0]]]}',
            '{"name": "Store B", "details": {"category": "wholesale", "id": 456}}',
        ),
    ]
    return spark.createDataFrame(data, ["point", "polygon", "metadata"])


def test_geo_functions(spark, test_data):
    result = test_data.selectExpr(
        "point_in_polygon(point, polygon) as is_inside"
    ).collect()

    assert result[0].is_inside == True
    assert result[1].is_inside == False


def test_json_functions(spark, test_data):
    result = test_data.selectExpr(
        "json_extract(metadata, '$.name') as store_name",
        "json_extract(metadata, '$.details.category') as category",
        "is_valid_json(metadata) as valid_json",
    ).collect()

    assert result[0].store_name == '"Store A"'
    assert result[0].category == '"retail"'
    assert result[0].valid_json == True

    assert result[1].store_name == '"Store B"'
    assert result[1].category == '"wholesale"'
    assert result[1].valid_json == True


def test_sql_query(spark, test_data):
    test_data.createOrReplaceTempView("stores")

    result = spark.sql("""
        SELECT 
            point_in_polygon(point, polygon) as is_inside,
            json_extract(metadata, '$.details.id') as store_id
        FROM stores
        WHERE point_in_polygon(point, polygon) = true
    """).collect()

    assert len(result) == 1
    assert result[0].store_id == "123"


def test_geohash_functions(spark, test_data):
    # Add test data with coordinates
    data = [
        (37.7749, -122.4194),  # San Francisco
        (40.7128, -74.0060),  # New York
    ]
    df = spark.createDataFrame(data, ["lat", "lon"])

    result = (
        df.selectExpr(
            "encode_geohash(lat, lon, 7) as hash",
            "lat as original_lat",
            "lon as original_lon",
        )
        .selectExpr("*", "decode_geohash(hash) as coords")
        .collect()
    )

    # Test San Francisco coordinates
    assert len(result[0].hash) == 7
    decoded_lat, decoded_lon = result[0].coords
    assert abs(decoded_lat - result[0].original_lat) / result[0].original_lat < 0.01
    assert (
        abs(decoded_lon - result[0].original_lon) / abs(result[0].original_lon) < 0.01
    )

    # Test New York coordinates
    assert len(result[1].hash) == 7
    decoded_lat, decoded_lon = result[1].coords
    assert abs(decoded_lat - result[1].original_lat) / result[1].original_lat < 0.01
    assert (
        abs(decoded_lon - result[1].original_lon) / abs(result[1].original_lon) < 0.01
    )