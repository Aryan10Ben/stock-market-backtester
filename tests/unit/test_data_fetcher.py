"""Tests for data fetcher and cache helpers."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from backtester.data.cache import cache_path, load_from_cache, save_to_cache
from backtester.data.fetcher import fetch_ohlcv
from backtester.data.loader import load_market_data_from_frame
from backtester.utils.exceptions import DataFetchError, DataValidationError


def _sample_frame(n: int = 80) -> pd.DataFrame:
    dates = pd.bdate_range("2023-01-03", periods=n)
    close = 100.0 + pd.Series(range(n), dtype=float).to_numpy() * 0.5
    frame = pd.DataFrame(
        {
            "Open": close - 0.2,
            "High": close + 0.5,
            "Low": close - 0.5,
            "Close": close,
            "Volume": 1_000_000.0,
        },
        index=dates,
    )
    frame.index.name = "Date"
    return frame


def test_fetch_uses_injected_downloader() -> None:
    expected = _sample_frame(30)

    def fake_download(*_args, **_kwargs):
        return expected.copy()

    result = fetch_ohlcv(
        "AAPL",
        date(2023, 1, 3),
        date(2023, 2, 15),
        downloader=fake_download,
        max_retries=1,
    )
    assert len(result) == 30
    assert list(result.columns) == ["Open", "High", "Low", "Close", "Volume"]


def test_fetch_retries_then_raises() -> None:
    calls = {"n": 0}

    def failing_download(*_args, **_kwargs):
        calls["n"] += 1
        raise ConnectionError("network down")

    with pytest.raises(DataFetchError, match="after 2 attempts"):
        fetch_ohlcv(
            "AAPL",
            date(2023, 1, 1),
            date(2023, 6, 1),
            downloader=failing_download,
            max_retries=2,
            backoff_seconds=0.01,
        )
    assert calls["n"] == 2


def test_fetch_empty_raises() -> None:
    def empty_download(*_args, **_kwargs):
        return pd.DataFrame()

    with pytest.raises(DataFetchError, match="No data returned"):
        fetch_ohlcv(
            "FAKE",
            date(2023, 1, 1),
            date(2023, 6, 1),
            downloader=empty_download,
            max_retries=1,
        )


def test_cache_roundtrip(tmp_path: Path) -> None:
    frame = _sample_frame(10)
    path = cache_path(tmp_path, "AAPL", date(2023, 1, 3), date(2023, 1, 20))
    save_to_cache(frame, path)
    loaded = load_from_cache(path)
    assert loaded is not None
    assert len(loaded) == 10
    pd.testing.assert_series_equal(
        loaded["Close"].reset_index(drop=True),
        frame["Close"].reset_index(drop=True),
    )


def test_cache_path_sanitizes_ticker(tmp_path: Path) -> None:
    path = cache_path(tmp_path, "BRK.B", date(2020, 1, 1), date(2021, 1, 1))
    assert path.name == "BRK.B_2020-01-01_2021-01-01.csv"
    assert path.parent == tmp_path


def test_cache_missing_returns_none(tmp_path: Path) -> None:
    assert load_from_cache(tmp_path / "missing.csv") is None


def test_pipeline_from_frame_fixture() -> None:
    fixture = Path("tests/fixtures/AAPL_sample.csv")
    frame = pd.read_csv(fixture, parse_dates=["Date"], index_col="Date")
    cleaned = load_market_data_from_frame(frame, min_bars=60, ticker="AAPL")
    assert len(cleaned) >= 60
    assert cleaned["Close"].isna().sum() == 0


def test_pipeline_rejects_too_few_bars() -> None:
    with pytest.raises(DataValidationError, match="Insufficient bars"):
        load_market_data_from_frame(_sample_frame(10), min_bars=60)
