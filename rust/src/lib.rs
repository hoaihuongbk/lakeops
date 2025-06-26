use pyo3::prelude::*;
mod geo;
mod json;

use geo::functions::{point_in_polygon, calculate_distance, encode_geohash, decode_geohash};
use json::functions::{json_extract, is_valid_json};

#[pymodule]
#[pyo3(name="_lakeops_udf")]
fn lakeops_udf(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(point_in_polygon, m)?)?;
    m.add_function(wrap_pyfunction!(calculate_distance, m)?)?;
    m.add_function(wrap_pyfunction!(json_extract, m)?)?;
    m.add_function(wrap_pyfunction!(is_valid_json, m)?)?;
    m.add_function(wrap_pyfunction!(encode_geohash, m)?)?;
    m.add_function(wrap_pyfunction!(decode_geohash, m)?)?;

    Ok(())
}