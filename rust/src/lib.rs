use pyo3::prelude::*;
mod geo;
mod json;

use geo::functions::{point_in_polygon, calculate_distance, encode_geohash, decode_geohash};
use json::functions::{json_extract, is_valid_json};

#[pymodule]
#[pyo3(name = "_lakeops_udf")]
fn lakeops_udf<'py>(_py: Python<'py>, m: &Bound<'py, PyModule>) -> PyResult<()> {
    m.add_wrapped(wrap_pyfunction!(point_in_polygon))?;
    m.add_wrapped(wrap_pyfunction!(calculate_distance))?;
    m.add_wrapped(wrap_pyfunction!(json_extract))?;
    m.add_wrapped(wrap_pyfunction!(is_valid_json))?;
    m.add_wrapped(wrap_pyfunction!(encode_geohash))?;
    m.add_wrapped(wrap_pyfunction!(decode_geohash))?;
    Ok(())
}