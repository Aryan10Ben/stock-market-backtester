"""Orchestrate fetch → cache → clean → validate for historical market data."""

from __future__ import annotations

import logging
from datetime import date

import pandas as pd

from backtester.config.settings import Settings
from backtester.data.cache import cache_path, load_from_cache, save_to_cache
from backtester.data.cleaner import clean_ohlcv
from backtester.data.fetcher import fetch_ohlcv
from backtester.data.validator import validate_ohlcv
from backtester.utils.exceptions import DataValidationError

logger = logging.getLogger("backtester.data")


def load_market_data(settings: Settings) -> pd.DataFrame:
    """
    Load validated, cleaned OHLCV data for the configured ticker and date range.

    Uses the local CSV cache when enabled. Always re-validates cached data so a
    corrupt cache cannot silently poison a backtest.
    """
    ticker = settings.ticker
    start = settings.start_date
    end = settings.end_date
    min_bars = settings.min_required_bars

    frame = _load_raw(ticker, start, end, settings)

    clean_result = clean_ohlcv(frame)
    cleaned = clean_result.frame

    report = validate_ohlcv(cleaned, min_bars=min_bars, ticker=ticker)
    report.raise_if_invalid()

    logger.info(
        "Market data ready: %s | %d bars | %s → %s",
        ticker,
        len(cleaned),
        cleaned.index.min().date() if len(cleaned) else "n/a",
        cleaned.index.max().date() if len(cleaned) else "n/a",
    )
    return cleaned


def _load_raw(
    ticker: str,
    start: date,
    end: date,
    settings: Settings,
) -> pd.DataFrame:
    """Load raw OHLCV from cache or the remote provider."""
    path = cache_path(settings.data.cache_dir, ticker, start, end)

    if settings.data.cache_enabled:
        cached = load_from_cache(path)
        if cached is not None:
            return cached

    frame = fetch_ohlcv(ticker, start, end)

    if settings.data.cache_enabled:
        save_to_cache(frame, path)

    return frame


def load_market_data_from_frame(
    frame: pd.DataFrame,
    *,
    min_bars: int,
    ticker: str = "FIXTURE",
) -> pd.DataFrame:
    """
    Clean and validate an in-memory DataFrame (used by tests and offline runs).

    Raises ``DataValidationError`` if the data is unusable after cleaning.
    """
    if frame is None:
        raise DataValidationError("Cannot load market data from None")

    clean_result = clean_ohlcv(frame)
    report = validate_ohlcv(clean_result.frame, min_bars=min_bars, ticker=ticker)
    report.raise_if_invalid()
    return clean_result.frame
