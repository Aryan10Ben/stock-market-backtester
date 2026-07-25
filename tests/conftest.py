"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from backtester.config.loader import load_settings
from backtester.config.settings import Settings, StrategySettings

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "default.yaml"
FIXTURE_CSV = PROJECT_ROOT / "tests" / "fixtures" / "AAPL_sample.csv"


@pytest.fixture
def default_config_path() -> Path:
    return DEFAULT_CONFIG


@pytest.fixture
def default_settings(default_config_path: Path) -> Settings:
    return load_settings(config_path=default_config_path)


@pytest.fixture
def sample_bars() -> pd.DataFrame:
    """80-bar OHLCV frame with a deterministic upward trend."""
    return pd.read_csv(FIXTURE_CSV, parse_dates=["Date"], index_col="Date")


@pytest.fixture
def crossover_bars() -> pd.DataFrame:
    """
    Synthetic bars with a clear golden cross then death cross.

    Flat low prices, sharp rally, then sharp decline — tuned for fast=3 / slow=8.
    """
    dates = pd.bdate_range("2023-01-03", periods=40)
    close = np.array(
        [50.0] * 10
        + list(np.linspace(50, 120, 15))
        + list(np.linspace(120, 40, 15))
    )
    return pd.DataFrame(
        {
            "Open": close - 0.2,
            "High": close + 0.5,
            "Low": close - 0.5,
            "Close": close,
            "Volume": 1_000_000.0,
        },
        index=dates,
    )


@pytest.fixture
def crossover_config() -> StrategySettings:
    """MA windows tuned for the crossover_bars fixture."""
    return StrategySettings(fast_window=3, slow_window=8, signal_on="close")


@pytest.fixture
def fast_strategy_config() -> StrategySettings:
    """Small MA windows for faster, more responsive tests."""
    return StrategySettings(fast_window=5, slow_window=20, signal_on="close")
