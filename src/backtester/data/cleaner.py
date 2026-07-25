"""Clean OHLCV data safely before backtesting."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd

from backtester.models.core import PRICE_COLUMNS, REQUIRED_COLUMNS

logger = logging.getLogger("backtester.data.cleaner")

# Forward-fill at most this many consecutive missing price rows.
DEFAULT_MAX_FFILL = 2


@dataclass(frozen=True)
class CleanResult:
    """Cleaned DataFrame plus a summary of what changed."""

    frame: pd.DataFrame
    rows_dropped: int
    rows_forward_filled: int


def clean_ohlcv(
    frame: pd.DataFrame,
    *,
    max_ffill: int = DEFAULT_MAX_FFILL,
) -> CleanResult:
    """
    Clean OHLCV data for backtesting.

    Steps:
    1. Keep only required columns.
    2. Sort by date and drop duplicate dates (keep first).
    3. Forward-fill short gaps in price columns (up to ``max_ffill`` bars).
    4. Drop any remaining rows with null OHLC prices.
    5. Coerce volume nulls to 0 (common for some holiday placeholders).
    """
    if frame.empty:
        return CleanResult(frame=frame.copy(), rows_dropped=0, rows_forward_filled=0)

    original_len = len(frame)
    cleaned = frame[list(REQUIRED_COLUMNS)].copy()
    cleaned = cleaned.sort_index()

    duplicate_count = int(cleaned.index.duplicated().sum())
    if duplicate_count:
        logger.warning("Dropping %d duplicate date rows", duplicate_count)
        cleaned = cleaned[~cleaned.index.duplicated(keep="first")]

    rows_forward_filled = 0
    if max_ffill > 0:
        price_nulls_before = int(cleaned[list(PRICE_COLUMNS)].isna().sum().sum())
        cleaned[list(PRICE_COLUMNS)] = cleaned[list(PRICE_COLUMNS)].ffill(limit=max_ffill)
        price_nulls_after = int(cleaned[list(PRICE_COLUMNS)].isna().sum().sum())
        rows_forward_filled = max(0, price_nulls_before - price_nulls_after)

        if rows_forward_filled:
            logger.info(
                "Forward-filled %d price cells (limit=%d consecutive bars)",
                rows_forward_filled,
                max_ffill,
            )

    before_drop = len(cleaned)
    cleaned = cleaned.dropna(subset=list(PRICE_COLUMNS))
    dropped_nulls = before_drop - len(cleaned)
    if dropped_nulls:
        logger.warning("Dropped %d rows with remaining null OHLC values", dropped_nulls)

    if "Volume" in cleaned.columns:
        cleaned["Volume"] = cleaned["Volume"].fillna(0)

    # Drop non-positive prices that slipped through
    invalid_prices = (cleaned[list(PRICE_COLUMNS)] <= 0).any(axis=1)
    invalid_count = int(invalid_prices.sum())
    if invalid_count:
        logger.warning("Dropped %d rows with non-positive prices", invalid_count)
        cleaned = cleaned[~invalid_prices]

    rows_dropped = original_len - len(cleaned)
    logger.info(
        "Cleaning complete: %d → %d bars (%d dropped)",
        original_len,
        len(cleaned),
        rows_dropped,
    )
    return CleanResult(
        frame=cleaned,
        rows_dropped=rows_dropped,
        rows_forward_filled=rows_forward_filled,
    )
