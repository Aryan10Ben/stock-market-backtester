"""Validate OHLCV DataFrames before they enter the backtest pipeline."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import pandas as pd

from backtester.models.core import PRICE_COLUMNS, REQUIRED_COLUMNS
from backtester.utils.exceptions import DataValidationError

logger = logging.getLogger("backtester.data.validator")

# Price jump larger than this fraction between consecutive closes is suspicious.
DEFAULT_PRICE_JUMP_THRESHOLD = 0.50


@dataclass
class ValidationReport:
    """Result of validating an OHLCV DataFrame."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    bar_count: int = 0

    def raise_if_invalid(self) -> None:
        if not self.is_valid:
            details = "; ".join(self.errors)
            raise DataValidationError(f"Data validation failed: {details}")


def validate_ohlcv(
    frame: pd.DataFrame,
    *,
    min_bars: int,
    ticker: str = "",
    price_jump_threshold: float = DEFAULT_PRICE_JUMP_THRESHOLD,
) -> ValidationReport:
    """
    Check that ``frame`` is usable for backtesting.

    Hard failures (errors) reject the dataset. Soft issues (warnings) are logged
    but do not block the pipeline.
    """
    errors: list[str] = []
    warnings: list[str] = []
    label = f" for {ticker}" if ticker else ""

    if frame is None or frame.empty:
        errors.append(f"Dataset{label} is empty")
        return ValidationReport(is_valid=False, errors=errors, bar_count=0)

    missing_cols = [col for col in REQUIRED_COLUMNS if col not in frame.columns]
    if missing_cols:
        errors.append(f"Missing required columns{label}: {missing_cols}")

    if not isinstance(frame.index, pd.DatetimeIndex):
        errors.append(f"Index must be DatetimeIndex{label}, got {type(frame.index).__name__}")
    else:
        if not frame.index.is_monotonic_increasing:
            errors.append(f"Dates are not sorted ascending{label}")
        if frame.index.has_duplicates:
            errors.append(f"Duplicate dates found{label}")

    # Only run numeric checks when columns exist
    available_price_cols = [c for c in PRICE_COLUMNS if c in frame.columns]
    if available_price_cols:
        price_data = frame[available_price_cols]
        if price_data.isna().any().any():
            null_counts = price_data.isna().sum()
            bad = null_counts[null_counts > 0].to_dict()
            errors.append(f"Null values in price columns{label}: {bad}")

        if (price_data <= 0).any().any():
            errors.append(f"Non-positive prices found{label}")

        if {"High", "Low"}.issubset(frame.columns):
            inverted = frame["High"] < frame["Low"]
            if inverted.any():
                errors.append(
                    f"{int(inverted.sum())} bars have High < Low{label}"
                )

        if {"High", "Low", "Open", "Close"}.issubset(frame.columns):
            outside_range = (
                (frame["Open"] > frame["High"])
                | (frame["Open"] < frame["Low"])
                | (frame["Close"] > frame["High"])
                | (frame["Close"] < frame["Low"])
            )
            if outside_range.any():
                warnings.append(
                    f"{int(outside_range.sum())} bars have Open/Close outside High-Low range{label}"
                )

    if "Volume" in frame.columns:
        zero_volume = (frame["Volume"] <= 0).sum()
        if zero_volume > 0:
            warnings.append(f"{int(zero_volume)} bars have zero/negative volume{label}")

    if "Close" in frame.columns and len(frame) > 1:
        returns = frame["Close"].pct_change(fill_method=None).abs()
        large_jumps = returns > price_jump_threshold
        jump_count = int(large_jumps.sum())
        if jump_count > 0:
            warnings.append(
                f"{jump_count} bars have close-to-close moves > "
                f"{price_jump_threshold:.0%}{label}"
            )

    bar_count = len(frame)
    if bar_count < min_bars:
        errors.append(
            f"Insufficient bars{label}: got {bar_count}, need at least {min_bars}"
        )

    is_valid = len(errors) == 0
    report = ValidationReport(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        bar_count=bar_count,
    )

    for warning in warnings:
        logger.warning(warning)
    if is_valid:
        logger.info("Validation passed%s: %d bars", label, bar_count)
    else:
        for error in errors:
            logger.error(error)

    return report
