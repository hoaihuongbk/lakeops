# Working with Google Sheets

LakeOps provides seamless integration with Google Sheets, allowing you to read and write data directly between your data lake and spreadsheets.

## Quick Start

```python
from lakeops.core.engines import GoogleSheetsEngine
from lakeops.core.secrets import DatabricksSecretManager

secrets = DatabricksSecretManager()
credentials = secrets.read("google_credentials", scope="production")
lake = GoogleSheetsEngine(credentials)
```

## Authentication
LakeOps uses Google Service Account for authentication with Google Sheets API. Here's how to set it up:

1. **Create Service Account**:
    - Go to [Google Cloud Console](https://console.cloud.google.com)
    - Create a new project or select existing one
    - Enable Google Sheets API for your project
    - Go to "IAM & Admin" > "Service Accounts"
    - Click "Create Service Account"
    - Download the JSON key file

2. **Store Service Account in LakeOps Secrets**:
```python
secrets.write("google_credentials", "<SECRETS FILE CONTENT>", scope="production")
```

## Features

### Reading data
```python
# Read from Google Sheet
df = lake.read(
    "1234567890abcdef", <-- Google Sheet ID
    format="gsheet",
)
```

### Writing data
```python
import polars as pl

# Write to Google Sheet
sales_data = pl.DataFrame({
    "date": ["2024-01-01", "2024-01-02"],
    "revenue": [1000, 1200]
})

lake.write(
    sales_data,
    "1234567890abcdef",  <-- Google Sheet ID
    format="gsheet",
)

```

## Best Practices
1. Use service accounts for production workloads
2. Use batch operations for large datasets