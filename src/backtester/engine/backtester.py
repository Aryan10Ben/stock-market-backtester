"""Main backtesting engine."""

from __future__ import annotations

import logging

import pandas as pd

from backtester.config.settings import Settings
from backtester.engine.executor import execute_signal
from backtester.engine.portfolio import Portfolio
from backtester.models.core import SignalAction
from backtester.models.result import BacktestResult, EquityPoint
from backtester.strategy.base import Strategy
from backtester.utils.exceptions import BacktestError

logger = logging.getLogger("backtester.engine.backtester")


class Backtester:
    """
    Bar-by-bar backtesting engine with next-bar execution.

    Timeline for each bar i:
      1. If signal[i-1] is BUY/SELL, execute on bar i (next-bar fill).
      2. Record end-of-day equity snapshot using bar i close.
    """

    def __init__(self, settings: Settings, strategy: Strategy) -> None:
        self.settings = settings
        self.strategy = strategy

    def run(self, bars: pd.DataFrame) -> BacktestResult:
        if bars is None or bars.empty:
            raise BacktestError("Cannot backtest on empty data")

        required = {"Open", "High", "Low", "Close", "Volume"}
        missing = required - set(bars.columns)
        if missing:
            raise BacktestError(f"Missing OHLCV columns: {sorted(missing)}")

        signals = self.strategy.generate_signals(bars)
        if len(signals) != len(bars):
            raise BacktestError(
                f"Strategy returned {len(signals)} signals for {len(bars)} bars"
            )

        portfolio = Portfolio(cash=self.settings.initial_cash)
        equity_curve: list[EquityPoint] = []

        first_close = float(bars["Close"].iloc[0])
        benchmark_shares = self.settings.initial_cash / first_close

        for i in range(len(bars)):
            bar = bars.iloc[i]
            close_price = float(bar["Close"])

            # Execute previous bar's signal at this bar's open/close — no look-ahead.
            if i > 0 and signals[i - 1].action != SignalAction.HOLD:
                execute_signal(portfolio, signals[i - 1], bar, self.settings)

            equity_curve.append(
                EquityPoint(
                    date=bars.index[i],
                    cash=portfolio.cash,
                    holdings_value=portfolio.holdings_value(close_price),
                    total_value=portfolio.total_value(close_price),
                    benchmark_value=benchmark_shares * close_price,
                    portfolio_qty=portfolio.quantity,
                )
            )

        final_value = equity_curve[-1].total_value
        logger.info(
            "Backtest complete: %d trades, final value $%.2f (%.2f%% return)",
            len(portfolio.trades),
            final_value,
            (final_value / self.settings.initial_cash - 1) * 100,
        )

        return BacktestResult(
            ticker=self.settings.ticker,
            start_date=bars.index[0],
            end_date=bars.index[-1],
            trades=portfolio.trades,
            signals=[s for s in signals if s.action != SignalAction.HOLD],
            equity_curve=equity_curve,
            price_data=bars,
        )
