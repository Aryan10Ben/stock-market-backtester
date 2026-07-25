"""Historical OHLCV data fetcher with robust fallback chain."""

from __future__ import annotations

import io
import logging
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Callable, Optional

import pandas as pd
import yfinance as yf
from curl_cffi import requests

from backtester.models.core import REQUIRED_COLUMNS
from backtester.utils.exceptions import DataFetchError

logger = logging.getLogger("backtester.data.fetcher")

DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_SECONDS = 2.0
SAMPLE_DATA_DIR = Path(__file__).parent / "sample"


def _normalize_frame(raw: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Normalize output into a flat OHLCV DataFrame indexed by date."""
    if raw.empty:
        raise DataFetchError(f"No data returned for ticker '{ticker}'.")

    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)

    missing = [col for col in REQUIRED_COLUMNS if col not in raw.columns]
    if missing:
        raise DataFetchError(f"Missing required columns for '{ticker}': {missing}")

    frame = raw[list(REQUIRED_COLUMNS)].copy()
    frame.index = pd.to_datetime(frame.index).tz_localize(None).normalize()
    frame.index.name = "Date"
    frame = frame.sort_index()
    return frame


def _fetch_yfinance(ticker: str, start: date, end: date) -> pd.DataFrame:
    """Fetch using yfinance with a curl_cffi Chrome impersonation session."""
    session = requests.Session(impersonate="chrome")
    fetch_end = end + timedelta(days=1)

    raw = yf.download(
        ticker,
        start=start.isoformat(),
        end=fetch_end.isoformat(),
        session=session,
        auto_adjust=True,
        progress=False,
        threads=False,
    )
    return _normalize_frame(raw, ticker)


def _fetch_stooq(ticker: str, start: date, end: date) -> pd.DataFrame:
    """Fetch from Stooq using curl_cffi as a fallback."""
    session = requests.Session(impersonate="chrome")
    url = f"https://stooq.com/q/d/l/?s={ticker.lower()}.us&i=d"

    resp = session.get(url, timeout=15)
    if resp.status_code != 200:
        raise DataFetchError(f"Stooq returned HTTP {resp.status_code}")

    try:
        raw = pd.read_csv(io.StringIO(resp.text), parse_dates=["Date"], index_col="Date")
    except Exception as e:
        raise DataFetchError(f"Failed to parse Stooq CSV: {e}")

    if raw.empty:
        raise DataFetchError(f"Stooq returned empty data for '{ticker}'")

    return _normalize_frame(raw, ticker)


def _load_bundled_sample(ticker: str, start: date, end: date) -> pd.DataFrame:
    """Load from bundled sample data if available."""
    path = SAMPLE_DATA_DIR / f"{ticker.upper()}.csv"
    if not path.exists():
        raise DataFetchError(f"No bundled sample data available for {ticker}")

    raw = pd.read_csv(path, parse_dates=["Date"], index_col="Date")
    frame = _normalize_frame(raw, ticker)

    mask = (frame.index.date >= start) & (frame.index.date <= end)
    filtered = frame.loc[mask]

    if filtered.empty:
        raise DataFetchError(f"Bundled sample data for {ticker} has no overlap with {start} to {end}")

    return filtered


def fetch_ohlcv(
    ticker: str,
    start: date,
    end: date,
    *,
    max_retries: int = DEFAULT_MAX_RETRIES,
    backoff_seconds: float = DEFAULT_BACKOFF_SECONDS,
    downloader: Optional[Callable] = None,
) -> pd.DataFrame:
    """
    Download daily OHLCV bars.
    Implements a resilient fallback chain:
    1. yfinance w/ curl_cffi
    2. Stooq API w/ curl_cffi
    3. Bundled sample data (AAPL, MSFT, NVDA, TSLA, SPY)
    """
    if start >= end:
        raise DataFetchError(f"start ({start}) must be before end ({end})")

    # 1. Try yfinance
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            logger.info("Fetching %s via yfinance (attempt %d/%d)", ticker, attempt, max_retries)
            if downloader is not None:
                raw = downloader(ticker, start=start.isoformat(), end=(end + timedelta(days=1)).isoformat())
                frame = _normalize_frame(raw, ticker)
            else:
                frame = _fetch_yfinance(ticker, start, end)
            logger.info("yfinance fetch successful: %d bars", len(frame))
            return frame
        except Exception as exc:
            last_error = exc
            logger.warning("yfinance attempt %d failed: %s", attempt, exc)
            if attempt >= max_retries and downloader is not None:
                # In test environments using a custom downloader, we raise after max retries
                raise DataFetchError(f"Downloader failed after {max_retries} attempts: {exc}") from exc
            if attempt < max_retries:
                time.sleep(backoff_seconds * (2 ** (attempt - 1)))

    if downloader is not None:
        raise DataFetchError(f"Failed to fetch data for '{ticker}' after {max_retries} attempts: {last_error}")

    logger.error("yfinance failed after %d attempts. Trying Stooq fallback...", max_retries)

    # 2. Try Stooq
    try:
        frame = _fetch_stooq(ticker, start, end)
        mask = (frame.index.date >= start) & (frame.index.date <= end)
        frame = frame.loc[mask]
        if frame.empty:
            raise DataFetchError("Stooq data empty for requested date range")
        logger.info("Stooq fallback successful: %d bars", len(frame))
        return frame
    except Exception as exc:
        logger.error("Stooq fallback failed: %s. Trying bundled samples...", exc)

    # 3. Try Bundled Samples
    try:
        frame = _load_bundled_sample(ticker, start, end)
        logger.warning(
            "LIVE DATA UNAVAILABLE. Serving %s from bundled historical sample. "
            "Values may not be up to date.", ticker
        )
        return frame
    except Exception as exc:
        raise DataFetchError(
            f"All data sources failed for '{ticker}'. "
            f"Last error: {exc}. "
            "Please check your internet connection, try a sample ticker (e.g. AAPL, MSFT), or upload a CSV."
        ) from exc
