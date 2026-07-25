from unittest.mock import patch

import pandas as pd
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)

@patch("api.main.load_market_data")
def test_successful_backtest(mock_load):
    """Test a basic successful backtest via API."""
    # Create some mock data
    dates = pd.date_range("2023-01-01", periods=100)
    mock_df = pd.DataFrame({
        "Open": [100.0] * 100,
        "High": [105.0] * 100,
        "Low": [95.0] * 100,
        "Close": [102.0] * 100,
        "Volume": [1000] * 100
    }, index=dates)
    mock_load.return_value = mock_df

    response = client.post("/api/backtest", json={
        "ticker": "AAPL",
        "start_date": "2023-01-01",
        "end_date": "2023-05-01",
        "fast_window": 10,
        "slow_window": 20
    })

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "metrics" in data
    assert "equity_curve" in data

    # Regression test for portfolio_qty in EquityPoint
    assert "portfolio_qty" in data["equity_curve"][0]

@patch("api.main.load_market_data")
def test_api_empty_data_handled_gracefully(mock_load):
    """Test that empty data returns a structured engine_error."""
    from backtester.utils.exceptions import BacktestError
    mock_load.side_effect = BacktestError("Cannot backtest on empty data")

    response = client.post("/api/backtest", json={
        "ticker": "AAPL",
        "start_date": "2023-01-01",
        "end_date": "2023-01-02",
    })

    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error_type"] == "engine_error"
    assert "Cannot backtest on empty data" in data["error_message"]
    assert "troubleshooting" in data

@patch("api.main.load_market_data")
def test_api_invalid_ticker_handled_gracefully(mock_load):
    """Test that invalid ticker (DataFetchError) returns network_error."""
    from backtester.utils.exceptions import DataFetchError
    mock_load.side_effect = DataFetchError("No data found for BADTICKER")

    response = client.post("/api/backtest", json={
        "ticker": "BADTICKER",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
    })

    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error_type"] == "network_error"
    assert "troubleshooting" in data

def test_api_config_validation_error():
    """Test that fast_window > slow_window throws input_error (if enforced).
    The Pydantic settings model will raise ConfigError or ValidationError."""
    response = client.post("/api/backtest", json={
        "ticker": "AAPL",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "fast_window": 50,
        "slow_window": 20  # Invalid
    })

    # Depending on how the settings class validates this, it might be a 400 input_error or standard FastAPI validation error.
    # Currently it seems StrategySettings might not strictly enforce fast < slow via ValueError, but if it does, it's covered.
    # We just ensure the app doesn't crash with 500.
    assert response.status_code in [400, 422]
