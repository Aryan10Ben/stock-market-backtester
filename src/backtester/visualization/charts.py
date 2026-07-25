"""Chart generation for backtest results."""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path

# Use a writable matplotlib config dir inside the project
_mpl_dir = Path(__file__).resolve().parents[3] / ".matplotlib"
_mpl_dir.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_mpl_dir))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from backtester.config.settings import Settings
from backtester.models.core import SignalAction
from backtester.models.result import BacktestResult
from backtester.strategy.base import Strategy

logger = logging.getLogger("backtester.visualization")


def create_output_dir(settings: Settings) -> Path:
    from backtester.utils.paths import resolve_path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = resolve_path(settings.output.dir) / f"{settings.ticker}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def plot_price_and_signals(
    result: BacktestResult,
    strategy: Strategy,
    settings: Settings,
    output_dir: Path,
) -> Path:
    bars = strategy.get_indicator_columns(result.price_data)
    fig, ax = plt.subplots(figsize=(14, 7))

    ax.plot(bars.index, bars["Close"], label="Close", color="#2563eb", linewidth=1.2)

    fast_col = f"MA_{settings.strategy.fast_window}"
    slow_col = f"MA_{settings.strategy.slow_window}"
    if fast_col in bars.columns:
        ax.plot(bars.index, bars[fast_col], label=f"MA {settings.strategy.fast_window}", alpha=0.8)
    if slow_col in bars.columns:
        ax.plot(bars.index, bars[slow_col], label=f"MA {settings.strategy.slow_window}", alpha=0.8)

    buy_dates = [s.date for s in result.signals if s.action == SignalAction.BUY]
    buy_prices = [s.price for s in result.signals if s.action == SignalAction.BUY]
    sell_dates = [s.date for s in result.signals if s.action == SignalAction.SELL]
    sell_prices = [s.price for s in result.signals if s.action == SignalAction.SELL]

    if buy_dates:
        ax.scatter(buy_dates, buy_prices, marker="^", color="#16a34a", s=80, label="Buy", zorder=5)
    if sell_dates:
        ax.scatter(sell_dates, sell_prices, marker="v", color="#dc2626", s=80, label="Sell", zorder=5)

    ax.set_title(f"{result.ticker} — Price & Signals ({settings.strategy.name})")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price ($)")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    path = output_dir / "price_signals.png"
    fig.savefig(path, dpi=settings.output.chart_dpi)
    plt.close(fig)
    logger.info("Saved price chart to %s", path)
    return path


def plot_equity_curve(result: BacktestResult, settings: Settings, output_dir: Path) -> Path:
    dates = [p.date for p in result.equity_curve]
    strategy_values = [p.total_value for p in result.equity_curve]
    benchmark_values = [p.benchmark_value for p in result.equity_curve]

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(dates, strategy_values, label="Strategy", color="#2563eb", linewidth=1.5)
    ax.plot(dates, benchmark_values, label="Buy & Hold", color="#94a3b8", linewidth=1.2, linestyle="--")
    ax.axhline(y=settings.initial_cash, color="#64748b", linestyle=":", alpha=0.5, label="Initial Capital")

    ax.set_title(f"{result.ticker} — Equity Curve")
    ax.set_xlabel("Date")
    ax.set_ylabel("Portfolio Value ($)")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    path = output_dir / "equity_curve.png"
    fig.savefig(path, dpi=settings.output.chart_dpi)
    plt.close(fig)
    logger.info("Saved equity curve to %s", path)
    return path


def plot_drawdown(result: BacktestResult, settings: Settings, output_dir: Path) -> Path:
    values = pd.Series(
        [p.total_value for p in result.equity_curve],
        index=[p.date for p in result.equity_curve],
    )
    rolling_max = values.cummax()
    drawdown = (values - rolling_max) / rolling_max * 100

    fig, ax = plt.subplots(figsize=(14, 4))
    ax.fill_between(drawdown.index, drawdown.values, 0, color="#dc2626", alpha=0.4)
    ax.plot(drawdown.index, drawdown.values, color="#dc2626", linewidth=1)
    ax.set_title(f"{result.ticker} — Drawdown")
    ax.set_xlabel("Date")
    ax.set_ylabel("Drawdown (%)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    path = output_dir / "drawdown.png"
    fig.savefig(path, dpi=settings.output.chart_dpi)
    plt.close(fig)
    logger.info("Saved drawdown chart to %s", path)
    return path


def generate_all_charts(
    result: BacktestResult,
    strategy: Strategy,
    settings: Settings,
    output_dir: Path | None = None,
) -> Path:
    if output_dir is None:
        output_dir = create_output_dir(settings)

    plot_price_and_signals(result, strategy, settings, output_dir)
    plot_equity_curve(result, settings, output_dir)
    plot_drawdown(result, settings, output_dir)
    return output_dir
