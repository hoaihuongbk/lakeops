import pytest
import polars as pl
from polars import Boolean, Utf8
from lakeops.udf import (
    point_in_polygon,
    calculate_distance,
    json_extract,
    is_valid_json,
    encode_geohash,
    decode_geohash,
)


def test_point_in_polygon():
    point_inside = '{"type":"Point","coordinates":[0.5,0.5]}'
    point_outside = '{"type":"Point","coordinates":[2.0,2.0]}'
    polygon = '{"type":"Polygon","coordinates":[[[0,0],[1,0],[1,1],[0,1],[0,0]]]}'

    assert point_in_polygon(point_inside, polygon) is True
    assert point_in_polygon(point_outside, polygon) is False


def test_calculate_distance():
    point1 = '{"type":"Point","coordinates":[0,0]}'
    point2 = '{"type":"Point","coordinates":[1,1]}'

    distance = calculate_distance(point1, point2)
    assert distance > 0
    assert isinstance(distance, float)


def test_json_functions():
    valid_json = '{"name": "Store A", "details": {"category": "retail", "id": 123}}'
    invalid_json = '{"broken": "json"'

    assert is_valid_json(valid_json) is True
    assert is_valid_json(invalid_json) is False

    category = json_extract(valid_json, "$.details.category")
    assert category == '"retail"'

    store_id = json_extract(valid_json, "$.details.id")
    assert store_id == "123"


def test_with_polars():
    data = [
        {
            "point": '{"type":"Point","coordinates":[0.5,0.5]}',
            "polygon": '{"type":"Polygon","coordinates":[[[0,0],[1,0],[1,1],[0,1],[0,0]]]}',
            "metadata": '{"name": "Store A", "details": {"category": "retail", "id": 123}}',
        },
        {
            "point": '{"type":"Point","coordinates":[2.0,2.0]}',
            "polygon": '{"type":"Polygon","coordinates":[[[0,0],[1,0],[1,1],[0,1],[0,0]]]}',
            "metadata": '{"name": "Store B", "details": {"category": "wholesale", "id": 456}}',
        },
    ]

    df = pl.DataFrame(data)

    df = df.with_columns(
        [
            pl.col("point")
            .map_elements(
                lambda x: point_in_polygon(x, df[0, "polygon"]), return_dtype=Boolean
            )
            .alias("is_inside"),
            pl.col("metadata")
            .map_elements(lambda x: json_extract(x, "$.name"), return_dtype=Utf8)
            .alias("store_name"),
            pl.col("metadata")
            .map_elements(is_valid_json, return_dtype=Boolean)
            .alias("valid_json"),
        ]
    )

    assert df["is_inside"][0] == True
    assert df["is_inside"][1] == False
    assert df["store_name"][0] == '"Store A"'
    assert df["valid_json"].all()


def test_geohash():
    lat, lon = 37.7749, -122.4194  # San Francisco
    hash = encode_geohash(lat, lon, 7)
    assert len(hash) == 7

    decoded_lat, decoded_lon = decode_geohash(hash)
    # Test relative difference
    assert abs(decoded_lat - lat) / lat < 0.01  # 1% tolerance
    assert abs(decoded_lon - lon) / abs(lon) < 0.01  # 1% tolerance
