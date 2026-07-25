"""Tests for OHLCV data cleaning."""

from __future__ import annotations

import numpy as np
import pandas as pd

from backtester.data.cleaner import clean_ohlcv


def _make_frame(n: int = 20) -> pd.DataFrame:
    dates = pd.bdate_range("2023-01-03", periods=n)
    close = 100.0 + np.arange(n, dtype=float)
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


def test_clean_drops_null_ohlc_rows() -> None:
    frame = _make_frame(10)
    frame.iloc[3, frame.columns.get_loc("Close")] = np.nan
    result = clean_ohlcv(frame, max_ffill=0)
    assert len(result.frame) == 9
    assert result.rows_dropped == 1
    assert result.frame["Close"].isna().sum() == 0


def test_clean_forward_fills_short_gaps() -> None:
    frame = _make_frame(10)
    frame.iloc[3, frame.columns.get_loc("Close")] = np.nan
    result = clean_ohlcv(frame, max_ffill=2)
    assert len(result.frame) == 10
    assert result.rows_forward_filled >= 1
    assert result.frame.iloc[3]["Close"] == result.frame.iloc[2]["Close"]


def test_clean_drops_duplicate_dates() -> None:
    frame = _make_frame(5)
    dup = pd.concat([frame, frame.iloc[[2]]])
    result = clean_ohlcv(dup)
    assert not result.frame.index.has_duplicates
    assert len(result.frame) == 5


def test_clean_drops_non_positive_prices() -> None:
    frame = _make_frame(10)
    frame.iloc[4, frame.columns.get_loc("Open")] = 0.0
    result = clean_ohlcv(frame)
    assert len(result.frame) == 9
    assert (result.frame[["Open", "High", "Low", "Close"]] > 0).all().all()


def test_clean_fills_null_volume_with_zero() -> None:
    frame = _make_frame(10)
    frame.iloc[2, frame.columns.get_loc("Volume")] = np.nan
    result = clean_ohlcv(frame)
    assert result.frame.iloc[2]["Volume"] == 0
