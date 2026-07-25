"""Adapter service connecting the web dashboard to the backtester core."""

from __future__ import annotations

import logging
from typing import Any, Optional

import pandas as pd

from backtester.config.loader import load_settings
from backtester.config.settings import Settings
from backtester.data.loader import load_market_data, load_market_data_from_frame
from backtester.engine.backtester import Backtester
from backtester.metrics.calculator import calculate_metrics
from backtester.models.result import BacktestResult
from backtester.strategy import create_strategy

logger = logging.getLogger("dashboard.services")


def run_dashboard_backtest(overrides: dict[str, Any], csv_frame: Optional[pd.DataFrame] = None) -> tuple[BacktestResult, Settings]:
    """
    Run a full backtest and return the result and the final settings.
    This mimics the CLI execution pipeline but avoids disk I/O.
    """
    # 1. Load settings with UI overrides
    settings = load_settings(cli_overrides=overrides)

    # 2. Fetch or load data
    if csv_frame is not None:
        logger.info("Dashboard loading data from CSV upload")
        frame = load_market_data_from_frame(
            csv_frame,
            min_bars=settings.min_required_bars,
            ticker=settings.ticker,
        )
    else:
        logger.info(f"Dashboard fetching data for {settings.ticker}")
        frame = load_market_data(settings)

    # 3. Strategy
    strategy = create_strategy(settings)

    # 4. Engine
    engine = Backtester(settings, strategy)
    result = engine.run(frame)

    # 5. Metrics
    calculate_metrics(result, settings)

    # 6. Attach indicator columns for charting
    result.price_data = strategy.get_indicator_columns(frame)

    return result, settings
