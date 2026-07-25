"""Console reporting and text outputs for backtest results."""

from __future__ import annotations

from typing import Any

from backtester import __version__
from backtester.config.settings import Settings
from backtester.models.core import SignalAction, TradeSide
from backtester.models.result import BacktestResult


def print_banner(settings: Settings) -> None:
    """Print a startup summary of the loaded configuration."""
    print()
    print("=" * 60)
    print("  Stock Market Backtesting System")
    print(f"  Version {__version__}")
    print("=" * 60)
    print(f"  Ticker:        {settings.ticker}")
    print(f"  Period:        {settings.start_date} → {settings.end_date}")
    print(f"  Initial Cash:  ${settings.initial_cash:,.2f}")
    print(f"  Strategy:      {settings.strategy.name}")
    print(f"    Fast MA:     {settings.strategy.fast_window}")
    print(f"    Slow MA:     {settings.strategy.slow_window}")
    print(f"  Commission:    {settings.commission_rate * 100:.2f}%")
    print(f"  Slippage:      {settings.slippage_bps} bps")
    print(f"  Execution:     next-bar {settings.execution.price}")
    print("=" * 60)
    print()


def print_data_summary(settings: Settings, frame: Any) -> None:
    """Print a short summary of loaded market data."""
    print("  Data Layer")
    print(f"  Bars loaded:   {len(frame)}")
    print(f"  Date span:     {frame.index.min().date()} → {frame.index.max().date()}")
    print(f"  Close range:   ${frame['Close'].min():.2f} – ${frame['Close'].max():.2f}")
    print(f"  Cache:         {'enabled' if settings.data.cache_enabled else 'disabled'}")
    print()


def print_strategy_summary(signals: list[Any]) -> None:
    """Print a summary of generated trading signals."""
    buys = [s for s in signals if s.action == SignalAction.BUY]
    sells = [s for s in signals if s.action == SignalAction.SELL]
    holds = len(signals) - len(buys) - len(sells)

    print("  Strategy Layer")
    print(f"  Signals:       {len(buys)} BUY | {len(sells)} SELL | {holds} HOLD")
    if buys:
        first = buys[0]
        print(f"  First BUY:     {first.date.date()} @ ${first.price:.2f}")
    if sells:
        first = sells[0]
        print(f"  First SELL:    {first.date.date()} @ ${first.price:.2f}")
    print()


def print_backtest_summary(settings: Settings, result: BacktestResult) -> None:
    """Print backtest engine and performance metrics."""
    metrics = result.metrics
    if metrics is None:
        return

    buys = sum(1 for t in result.trades if t.side == TradeSide.BUY)
    sells = sum(1 for t in result.trades if t.side == TradeSide.SELL)

    print("  Backtest Engine")
    print(f"  Trades:        {metrics.num_trades} round-trips ({buys} buys, {sells} sells)")
    print(f"  Final Value:   ${metrics.final_value:,.2f}")
    print()
    print("  Performance Metrics")
    print(f"  Total Return:  {metrics.total_return * 100:+.2f}%")
    print(f"  Buy & Hold:    {metrics.buy_and_hold_return * 100:+.2f}%")
    print(f"  Excess Return: {metrics.excess_return * 100:+.2f}%")
    print(f"  CAGR:          {metrics.cagr * 100:+.2f}%")
    print(f"  Sharpe Ratio:  {metrics.sharpe_ratio:.2f}")
    print(f"  Max Drawdown:  {metrics.max_drawdown * 100:.2f}%")
    print(f"  Win Rate:      {metrics.win_rate * 100:.1f}% ({metrics.num_winning_trades}W / {metrics.num_losing_trades}L)")
    print()
