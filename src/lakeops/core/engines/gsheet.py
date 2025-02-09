from typing import Any, Dict, Optional

import polars as pl

from .base import Engine


class GoogleSheetsEngine(Engine):
    def __init__(self, credentials: Dict[str, Any]):
        import gspread

        self.gc = gspread.service_account_from_dict(credentials)

    def read(
        self,
        path: str,
        format: str = "delta",
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        ## Open the sheet by ID or URL
        ## Select the first worksheet
        ## Load all data into a Polars DataFrame
        if self.is_storage_path(path):
            sh = self.gc.open_by_url(path)
        else:
            sh = self.gc.open_by_key(path)

        ws = sh.get_worksheet(0)
        records = ws.get_all_records()
        return pl.DataFrame(records)

    def write(
        self,
        data: Any,
        path: str,
        format: str = "delta",
        mode: str = "overwrite",
        options: Optional[Dict[str, Any]] = None,
    ):
        ## Convert the Polars DataFrame to a numpy array
        ## Open the sheet by ID or URL
        ## Select the first worksheet
        ## Write the numpy array to the sheet
        if self.is_storage_path(path):
            sh = self.gc.open_by_url(path)
        else:
            sh = self.gc.open_by_key(path)

        ws = sh.get_worksheet(0)

        # Get column names and data in one list
        headers = data.columns
        values = data.to_numpy().tolist()
        all_data = [headers] + values

        # Update worksheet with headers and data
        ws.update(all_data)

    def execute(self, sql: str, **kwargs) -> Any:
        raise NotImplementedError(
            "GoogleSheetEngine does not support execute SQL directly"
        )