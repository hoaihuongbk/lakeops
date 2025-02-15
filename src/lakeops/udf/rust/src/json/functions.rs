use pyo3::prelude::*;
use serde_json::Value;

#[pyfunction]
pub fn json_extract(json_str: &str, path: &str) -> PyResult<Option<String>> {
    let value: Value = serde_json::from_str(json_str)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid JSON: {}", e)))?;

    let found = jsonpath_lib::select(&value, path)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("JSONPath evaluation error: {}", e)))?;

    if found.is_empty() {
        Ok(None)
    } else {
        Ok(Some(found[0].to_string()))
    }
}

#[pyfunction]
pub fn is_valid_json(json_str: &str) -> bool {
    serde_json::from_str::<Value>(json_str).is_ok()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_json_extract() {
        let json = r#"{"name":"test","nested":{"value":42}}"#;
        let result = json_extract(json, "$.nested.value").unwrap();
        assert_eq!(result, Some("42".to_string()));
    }

    #[test]
    fn test_is_valid_json() {
        assert!(is_valid_json(r#"{"valid":true}"#));
        assert!(!is_valid_json(r#"{"invalid":}"#));
    }
}
