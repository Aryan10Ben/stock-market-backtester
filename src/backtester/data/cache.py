"""Local CSV cache for fetched OHLCV data."""

from __future__ import annotations

import logging
import re
from datetime import date
from pathlib import Path

import pandas as pd

logger = logging.getLogger("backtester.data.cache")

# Safe filename characters only — prevents path traversal via ticker strings.
_SAFE_TOKEN = re.compile(r"[^A-Z0-9._-]")


def _sanitize_token(value: str) -> str:
    return _SAFE_TOKEN.sub("_", value.upper())


from backtester.utils.paths import resolve_path


def cache_path(cache_dir: str | Path, ticker: str, start: date, end: date) -> Path:
    """Build a deterministic cache file path for a ticker/date range."""
    name = f"{_sanitize_token(ticker)}_{start.isoformat()}_{end.isoformat()}.csv"
    return resolve_path(cache_dir) / name


def load_from_cache(path: Path) -> pd.DataFrame | None:
    """Load a cached DataFrame, or return None if the cache file is missing/unreadable."""
    if not path.exists():
        return None

    try:
        frame = pd.read_csv(path, parse_dates=["Date"], index_col="Date")
        if frame.empty:
            logger.warning("Cache file is empty, ignoring: %s", path)
            return None
        logger.info("Loaded %d bars from cache: %s", len(frame), path)
        return frame
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        logger.warning("Failed to read cache file %s: %s", path, exc)
        return None


def save_to_cache(frame: pd.DataFrame, path: Path) -> None:
    """Persist a DataFrame to the cache directory as CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    # Write via a temporary sibling, then replace — avoids partial writes.
    temp_path = path.with_suffix(".csv.tmp")
    try:
        frame.to_csv(temp_path, index=True, index_label="Date")
        temp_path.replace(path)
        logger.info("Cached %d bars to %s", len(frame), path)
    except OSError as exc:
        logger.warning("Failed to write cache file %s: %s", path, exc)
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
