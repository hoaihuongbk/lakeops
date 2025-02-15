use geo::{Point, Polygon, Contains, LineString};
use geo::algorithm::haversine_distance::HaversineDistance;
use geohash::Coord;
use pyo3::prelude::*;
use serde_json::Value;

#[pyfunction]
pub fn point_in_polygon(point_str: &str, polygon_str: &str) -> PyResult<bool> {
    let point = parse_geojson_point(point_str)?;
    let polygon = parse_geojson_polygon(polygon_str)?;
    Ok(polygon.contains(&point))
}

#[pyfunction]
pub fn calculate_distance(point1_str: &str, point2_str: &str) -> PyResult<f64> {
    let point1 = parse_geojson_point(point1_str)?;
    let point2 = parse_geojson_point(point2_str)?;
    Ok(point1.haversine_distance(&point2))
}

#[pyfunction]
pub fn encode_geohash(lat: f64, lon: f64, precision: usize) -> PyResult<String> {
    let coord = Coord { x: lon, y: lat };
    geohash::encode(coord, precision)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))
}

#[pyfunction]
pub fn decode_geohash(hash: &str) -> PyResult<(f64, f64)> {
    let (coord, _, _) = geohash::decode(hash)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
    Ok((coord.y, coord.x))
}

fn parse_geojson_point(json_str: &str) -> PyResult<Point<f64>> {
    let v: Value = serde_json::from_str(json_str)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid JSON: {}", e)))?;

    match &v {
        Value::Object(obj) => {
            if obj.get("type").and_then(Value::as_str) != Some("Point") {
                return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("GeoJSON must be of type Point"));
            }

            if let Some(Value::Array(coords)) = obj.get("coordinates") {
                if coords.len() != 2 {
                    return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Point coordinates must have exactly 2 values"));
                }

                let x = coords[0].as_f64()
                    .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("Invalid longitude value"))?;
                let y = coords[1].as_f64()
                    .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("Invalid latitude value"))?;

                Ok(Point::new(x, y))
            } else {
                Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Invalid Point coordinates format"))
            }
        },
        _ => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Invalid GeoJSON format"))
    }
}

fn parse_geojson_polygon(json_str: &str) -> PyResult<Polygon<f64>> {
    let v: Value = serde_json::from_str(json_str)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid JSON: {}", e)))?;

    match &v {
        Value::Object(obj) => {
            if obj.get("type").and_then(Value::as_str) != Some("Polygon") {
                return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("GeoJSON must be of type Polygon"));
            }

            if let Some(Value::Array(rings)) = obj.get("coordinates") {
                if rings.is_empty() {
                    return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Polygon must have at least one ring"));
                }

                let exterior: Vec<(f64, f64)> = parse_ring(&rings[0])?;

                let mut interiors: Vec<LineString<f64>> = Vec::new();
                for ring in rings.iter().skip(1) {
                    let coords = parse_ring(ring)?;
                    interiors.push(LineString::from(coords));
                }

                Ok(Polygon::new(LineString::from(exterior), interiors))
            } else {
                Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Invalid Polygon coordinates format"))
            }
        },
        _ => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Invalid GeoJSON format"))
    }
}

fn parse_ring(ring: &Value) -> PyResult<Vec<(f64, f64)>> {
    if let Value::Array(coords) = ring {
        let points: Result<Vec<(f64, f64)>, PyErr> = coords.iter()
            .map(|coord| {
                if let Value::Array(point) = coord {
                    if point.len() != 2 {
                        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Each coordinate must have exactly 2 values"));
                    }
                    let x = point[0].as_f64()
                        .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("Invalid x coordinate"))?;
                    let y = point[1].as_f64()
                        .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("Invalid y coordinate"))?;
                    Ok((x, y))
                } else {
                    Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Invalid coordinate format"))
                }
            })
            .collect();
        points
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Ring must be an array of coordinates"))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_point_parsing() {
        let point_str = r#"{"type":"Point","coordinates":[1.0,2.0]}"#;
        let point = parse_geojson_point(point_str).unwrap();
        assert_eq!(point.x(), 1.0);
        assert_eq!(point.y(), 2.0);
    }

    #[test]
    fn test_polygon_parsing() {
        let polygon_str = r#"{"type":"Polygon","coordinates":[[[0.0,0.0],[1.0,0.0],[1.0,1.0],[0.0,1.0],[0.0,0.0]]]}"#;
        let polygon = parse_geojson_polygon(polygon_str).unwrap();
        assert_eq!(polygon.exterior().points().count(), 5);
    }

    #[test]
    fn test_point_in_polygon() {
        let point_str = r#"{"type":"Point","coordinates":[0.5,0.5]}"#;
        let polygon_str = r#"{"type":"Polygon","coordinates":[[[0.0,0.0],[1.0,0.0],[1.0,1.0],[0.0,1.0],[0.0,0.0]]]}"#;
        assert!(point_in_polygon(point_str, polygon_str).unwrap());
    }

    #[test]
    fn test_geohash_encode() {
        let lat = 37.7749;
        let lon = -122.4194;
        let hash = encode_geohash(lat, lon, 7).unwrap();
        assert_eq!(hash.len(), 7);
    }

    #[test]
    fn test_geohash_decode() {
        let hash = "9q8yyk8";  // San Francisco area
        let (lat, lon) = decode_geohash(hash).unwrap();
        assert!((lat - 37.7749).abs() < 0.01);
        assert!((lon - (-122.4194)).abs() < 0.01);
    }

    #[test]
    fn test_geohash_roundtrip() {
        let original_lat = 37.7749;
        let original_lon = -122.4194;
        let hash = encode_geohash(original_lat, original_lon, 7).unwrap();
        let (decoded_lat, decoded_lon) = decode_geohash(&hash).unwrap();

        assert!((original_lat - decoded_lat).abs() < 0.01);
        assert!((original_lon - decoded_lon).abs() < 0.01);
    }
}
