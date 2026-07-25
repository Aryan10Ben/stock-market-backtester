"""Backtest result models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

import pandas as pd

from backtester.models.core import Signal, Trade


@dataclass
class EquityPoint:
    date: datetime
    cash: float
    holdings_value: float
    total_value: float
    benchmark_value: float
    portfolio_qty: int = 0


@dataclass
class PerformanceMetrics:
    total_return: float
    buy_and_hold_return: float
    excess_return: float
    cagr: float
    win_rate: float
    max_drawdown: float
    sharpe_ratio: float
    num_trades: int
    num_winning_trades: int
    num_losing_trades: int
    initial_cash: float
    final_value: float
    benchmark_final_value: float


@dataclass
class BacktestResult:
    ticker: str
    start_date: datetime
    end_date: datetime
    trades: list[Trade] = field(default_factory=list)
    signals: list[Signal] = field(default_factory=list)
    equity_curve: list[EquityPoint] = field(default_factory=list)
    price_data: pd.DataFrame | None = None
    metrics: PerformanceMetrics | None = None
