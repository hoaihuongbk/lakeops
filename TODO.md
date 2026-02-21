# TODO List

## Secret Management
- [x] **Vault Authentication Enhancements**
    - [x] Support JWT/OIDC authentication method.
    - [x] Support Kubernetes (K8s) authentication method for containerized workloads.
    - [ ] Support AppRole for machine-to-machine authentication.
- [ ] **Secret Rotation**
    - Implement a lifecycle management interface for rotating secrets.
- [ ] **Cloud Provider Backends**
    - AWS Secrets Manager implementation.
    - Azure Key Vault implementation.
    - GCP Secret Manager implementation.

## Engines & Connectivity
- [ ] **Databricks Spark Connect**
    - Support Databricks-specific Spark Connect implementation (which requires specific headers and session management compared to OSS Spark Connect).
- [ ] **Engine Performance**
    - Optimize Polars to Spark DataFrame conversion for large datasets.
    - Implement lazy execution where possible across all engines to optimize pushdown filters.

## Rust Extensions (UDFs)
- [ ] **New UDFs**
    - Add H3 indexing support for geospatial operations.
    - Add more complex JSON transformation functions.
- [ ] **Vectorization**
    - Improve performance of existing Rust UDFs by leveraging Arrow vectorization more effectively.

## Infrastructure & DX
- [ ] **Testing**
    - Integrate a local Hashicorp Vault container for integration testing.
    - Add more comprehensive integration tests for different Spark versions.
- [ ] **Documentation**
    - Add more end-to-end examples for multi-engine workflows (e.g., reading from GSheet and writing to Delta Lake via Spark).
