"""Command-line interface for the backtesting system."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path
from typing import Any

from backtester import __version__
from backtester.config.loader import load_settings
from backtester.data import load_market_data
from backtester.data.loader import load_market_data_from_frame
from backtester.engine import Backtester
from backtester.metrics import calculate_metrics
from backtester.strategy import create_strategy
from backtester.utils.exceptions import BacktesterError, ConfigError
from backtester.utils.logging import setup_logging
from backtester.visualization.charts import create_output_dir, generate_all_charts
from backtester.visualization.reporter import (
    print_backtest_summary,
    print_banner,
    print_data_summary,
    print_strategy_summary,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="backtester",
        description="Stock Market Backtesting System — simulate trading strategies on historical data.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to YAML configuration file (optional)",
    )
    parser.add_argument("--ticker", type=str, help="Stock ticker symbol (e.g. AAPL)")
    parser.add_argument("--start", type=str, dest="start_date", help="Backtest start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, dest="end_date", help="Backtest end date (YYYY-MM-DD)")
    parser.add_argument(
        "--initial-cash",
        type=float,
        help="Starting capital in USD",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        help="Optional path to a local OHLCV CSV (skips remote fetch)",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"backtester {__version__}",
    )
    return parser


def _cli_overrides_from_args(args: argparse.Namespace) -> dict[str, Any]:
    """Build a nested override dict from parsed CLI arguments."""
    overrides: dict[str, Any] = {}

    if args.ticker is not None:
        overrides["ticker"] = args.ticker
    if args.start_date is not None:
        overrides["start_date"] = date.fromisoformat(args.start_date)
    if args.end_date is not None:
        overrides["end_date"] = date.fromisoformat(args.end_date)
    if args.initial_cash is not None:
        overrides["initial_cash"] = args.initial_cash
    if args.log_level is not None:
        overrides["logging"] = {"level": args.log_level}

    return overrides





def _load_csv(path: Path) -> Any:
    """Load a local OHLCV CSV with a Date index."""
    import pandas as pd

    if not path.exists():
        raise BacktesterError(f"CSV file not found: {path}")
    if path.suffix.lower() != ".csv":
        raise BacktesterError(f"Expected a .csv file, got: {path}")

    frame = pd.read_csv(path, parse_dates=["Date"], index_col="Date")
    if frame.empty:
        raise BacktesterError(f"CSV file is empty: {path}")
    return frame


def main(argv: list[str] | None = None) -> int:
    """Entry point: parse args, load config, fetch data, print summary."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        cli_overrides = _cli_overrides_from_args(args)
        settings = load_settings(config_path=args.config, cli_overrides=cli_overrides)
    except (ConfigError, ValueError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1

    logger = setup_logging(
        level=settings.logging.level,
        log_dir=settings.logging.log_dir,
        log_file=settings.logging.log_file,
    )
    logger.info("Backtester started")
    logger.info(
        "Config loaded: ticker=%s, period=%s to %s",
        settings.ticker,
        settings.start_date,
        settings.end_date,
    )
    logger.debug("Full settings: %s", settings.model_dump())

    print_banner(settings)

    try:
        if args.csv is not None:
            logger.info("Loading market data from CSV: %s", args.csv)
            raw = _load_csv(args.csv)
            frame = load_market_data_from_frame(
                raw,
                min_bars=settings.min_required_bars,
                ticker=settings.ticker,
            )
        else:
            frame = load_market_data(settings)
    except BacktesterError as exc:
        logger.error("Data layer failed: %s", exc)
        print(f"Data error: {exc}", file=sys.stderr)
        return 1

    print_data_summary(settings, frame)

    try:
        strategy = create_strategy(settings)
        signals = strategy.generate_signals(frame)
    except (BacktesterError, ValueError) as exc:
        logger.error("Strategy layer failed: %s", exc)
        print(f"Strategy error: {exc}", file=sys.stderr)
        return 1

    print_strategy_summary(signals)

    try:
        engine = Backtester(settings, strategy)
        result = engine.run(frame)
        calculate_metrics(result, settings)

        output_dir = create_output_dir(settings)
        generate_all_charts(result, strategy, settings, output_dir)
        print(f"  Charts saved to: {output_dir}")
        print()
    except (BacktesterError, ValueError) as exc:
        logger.error("Backtest failed: %s", exc)
        print(f"Backtest error: {exc}", file=sys.stderr)
        return 1

    print_backtest_summary(settings, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
