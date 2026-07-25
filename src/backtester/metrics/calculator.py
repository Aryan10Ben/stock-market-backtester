"""Performance metrics calculation."""

from __future__ import annotations

import logging
from datetime import datetime

import numpy as np
import pandas as pd

from backtester.config.settings import Settings
from backtester.models.core import Trade, TradeSide
from backtester.models.result import BacktestResult, PerformanceMetrics

logger = logging.getLogger("backtester.metrics")


def calculate_metrics(result: BacktestResult, settings: Settings) -> PerformanceMetrics:
    """Compute performance statistics and attach them to ``result.metrics``."""
    if not result.equity_curve:
        raise ValueError("Cannot calculate metrics without an equity curve")

    initial_cash = settings.initial_cash
    final_value = result.equity_curve[-1].total_value
    benchmark_final = result.equity_curve[-1].benchmark_value

    total_return = (final_value - initial_cash) / initial_cash
    buy_and_hold_return = (benchmark_final - initial_cash) / initial_cash
    excess_return = total_return - buy_and_hold_return

    cagr = _calculate_cagr(initial_cash, final_value, result.start_date, result.end_date)
    max_drawdown = _calculate_max_drawdown(result)
    sharpe = _calculate_sharpe(result, settings)
    win_rate, num_wins, num_losses = _calculate_win_rate(result.trades)
    num_round_trips = num_wins + num_losses

    metrics = PerformanceMetrics(
        total_return=total_return,
        buy_and_hold_return=buy_and_hold_return,
        excess_return=excess_return,
        cagr=cagr,
        win_rate=win_rate,
        max_drawdown=max_drawdown,
        sharpe_ratio=sharpe,
        num_trades=num_round_trips,
        num_winning_trades=num_wins,
        num_losing_trades=num_losses,
        initial_cash=initial_cash,
        final_value=final_value,
        benchmark_final_value=benchmark_final,
    )

    result.metrics = metrics
    logger.info(
        "Metrics: return=%.2f%%, buy-hold=%.2f%%, sharpe=%.2f, max_dd=%.2f%%",
        total_return * 100,
        buy_and_hold_return * 100,
        sharpe,
        max_drawdown * 100,
    )
    return metrics


def _calculate_cagr(
    initial: float, final: float, start: datetime, end: datetime
) -> float:
    years = (end - start).days / 365.25
    if years <= 0 or initial <= 0 or final <= 0:
        return 0.0
    return (final / initial) ** (1 / years) - 1


def _calculate_max_drawdown(result: BacktestResult) -> float:
    values = pd.Series([p.total_value for p in result.equity_curve])
    rolling_max = values.cummax()
    drawdown = (values - rolling_max) / rolling_max
    return float(drawdown.min())


def _calculate_sharpe(result: BacktestResult, settings: Settings) -> float:
    values = pd.Series([p.total_value for p in result.equity_curve])
    daily_returns = values.pct_change(fill_method=None).dropna()
    if daily_returns.empty or daily_returns.std() == 0:
        return 0.0

    trading_days = settings.metrics.trading_days_per_year
    rf_daily = settings.metrics.risk_free_rate / trading_days
    excess = daily_returns - rf_daily
    return float(excess.mean() / excess.std() * np.sqrt(trading_days))


def _calculate_win_rate(trades: list[Trade]) -> tuple[float, int, int]:
    """Win rate from completed round trips (BUY followed by SELL)."""
    wins = 0
    losses = 0
    i = 0
    while i < len(trades) - 1:
        if trades[i].side == TradeSide.BUY and trades[i + 1].side == TradeSide.SELL:
            buy_cost = trades[i].total_cost
            sell_proceeds = trades[i + 1].total_cost
            pnl = sell_proceeds - buy_cost
            if pnl > 0:
                wins += 1
            else:
                losses += 1
            i += 2
        else:
            i += 1

    total = wins + losses
    win_rate = wins / total if total > 0 else 0.0
    return win_rate, wins, losses
