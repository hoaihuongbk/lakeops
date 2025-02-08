import pytest
import polars as pl
from unittest.mock import Mock, patch
from lakeops.core.engines.gsheet import GoogleSheetsEngine


@pytest.fixture
def mock_credentials():
    return {
        "type": "service_account",
        "project_id": "test-project",
        "private_key": "test-key",
        "client_email": "test@email.com",
    }


@pytest.fixture
def mock_worksheet_data():
    return [{"col1": 1, "col2": "a"}, {"col1": 2, "col2": "b"}]


@pytest.fixture
def mock_gspread(mock_worksheet_data):
    # Create mock worksheet with real data return value
    mock_ws = Mock()
    mock_ws.get_all_records.return_value = mock_worksheet_data
    mock_ws.update = Mock()

    mock_sh = Mock()
    mock_sh.get_worksheet = Mock(return_value=mock_ws)

    mock_client = Mock()
    mock_client.open_by_url = Mock(return_value=mock_sh)
    mock_client.open_by_key = Mock(return_value=mock_sh)

    return mock_client


class TestGoogleSheetsEngine:
    @patch("gspread.service_account_from_dict")
    def test_init(self, mock_service_account, mock_credentials):
        engine = GoogleSheetsEngine(mock_credentials)
        mock_service_account.assert_called_once_with(mock_credentials)

    @patch("gspread.service_account_from_dict")
    def test_read_sheet(
        self, mock_service_account, mock_gspread, mock_credentials, mock_worksheet_data
    ):
        mock_service_account.return_value = mock_gspread

        engine = GoogleSheetsEngine(mock_credentials)
        df = engine.read("test_sheet_id", "sheet")

        assert isinstance(df, pl.DataFrame)
        assert df.shape == (2, 2)
        assert df.to_dict(as_series=False) == {"col1": [1, 2], "col2": ["a", "b"]}

    @patch("gspread.service_account_from_dict")
    def test_write_sheet(self, mock_service_account, mock_gspread, mock_credentials):
        mock_service_account.return_value = mock_gspread

        # Create test DataFrame to write
        test_df = pl.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})

        engine = GoogleSheetsEngine(mock_credentials)
        engine.write(test_df, "test_sheet_id", "sheet")

        # Get the mock worksheet and verify update was called with headers + data
        mock_worksheet = (
            mock_gspread.open_by_key.return_value.get_worksheet.return_value
        )
        expected_data = [
            ["col1", "col2"],  # Headers
            [1, "a"],  # Data row 1
            [2, "b"],  # Data row 2
        ]
        mock_worksheet.update.assert_called_once_with(expected_data)

    @patch("gspread.service_account_from_dict")
    def test_execute_raises_error(self, mock_credentials):
        engine = GoogleSheetsEngine(mock_credentials)
        with pytest.raises(NotImplementedError):
            engine.execute("SELECT * FROM table")
