"""Tests for OHLCV data validation."""

from __future__ import annotations

import pandas as pd
import pytest

from backtester.data.validator import validate_ohlcv
from backtester.utils.exceptions import DataValidationError


def _make_frame(n: int = 60) -> pd.DataFrame:
    dates = pd.bdate_range("2023-01-03", periods=n)
    close = 100.0 + pd.Series(range(n), dtype=float).to_numpy()
    return pd.DataFrame(
        {
            "Open": close - 0.1,
            "High": close + 0.5,
            "Low": close - 0.5,
            "Close": close,
            "Volume": 1_000_000.0,
        },
        index=dates,
    )


def test_valid_frame_passes() -> None:
    report = validate_ohlcv(_make_frame(60), min_bars=50, ticker="TEST")
    assert report.is_valid
    assert report.bar_count == 60
    assert report.errors == []


def test_empty_frame_fails() -> None:
    report = validate_ohlcv(pd.DataFrame(), min_bars=10)
    assert not report.is_valid
    with pytest.raises(DataValidationError):
        report.raise_if_invalid()


def test_missing_columns_fail() -> None:
    frame = _make_frame(60).drop(columns=["Volume"])
    report = validate_ohlcv(frame, min_bars=10)
    assert not report.is_valid
    assert any("Missing required columns" in e for e in report.errors)


def test_non_positive_prices_fail() -> None:
    frame = _make_frame(60)
    frame.iloc[5, frame.columns.get_loc("Close")] = -1.0
    report = validate_ohlcv(frame, min_bars=10)
    assert not report.is_valid
    assert any("Non-positive" in e for e in report.errors)


def test_unsorted_dates_fail() -> None:
    frame = _make_frame(60).iloc[::-1]
    report = validate_ohlcv(frame, min_bars=10)
    assert not report.is_valid
    assert any("not sorted" in e for e in report.errors)


def test_insufficient_bars_fail() -> None:
    report = validate_ohlcv(_make_frame(20), min_bars=50, ticker="TEST")
    assert not report.is_valid
    assert any("Insufficient bars" in e for e in report.errors)


def test_zero_volume_warns_but_passes() -> None:
    frame = _make_frame(60)
    frame.iloc[0, frame.columns.get_loc("Volume")] = 0
    report = validate_ohlcv(frame, min_bars=10)
    assert report.is_valid
    assert any("volume" in w.lower() for w in report.warnings)


def test_large_price_jump_warns() -> None:
    frame = _make_frame(60)
    frame.iloc[10, frame.columns.get_loc("Close")] = frame.iloc[9]["Close"] * 2.0
    # Keep High/Low consistent so only jump warning fires
    frame.iloc[10, frame.columns.get_loc("High")] = frame.iloc[10]["Close"] + 0.5
    frame.iloc[10, frame.columns.get_loc("Low")] = frame.iloc[10]["Close"] - 0.5
    frame.iloc[10, frame.columns.get_loc("Open")] = frame.iloc[10]["Close"]
    report = validate_ohlcv(frame, min_bars=10, price_jump_threshold=0.50)
    assert report.is_valid
    assert any("moves >" in w for w in report.warnings)
