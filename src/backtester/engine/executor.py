"""Order execution logic."""

from __future__ import annotations

import logging

import pandas as pd

from backtester.config.settings import Settings
from backtester.engine.portfolio import Portfolio
from backtester.models.core import Signal, SignalAction, Trade

logger = logging.getLogger("backtester.engine.executor")

_EXECUTION_COLUMN = {
    "open": "Open",
    "close": "Close",
}


def get_execution_price(bar: pd.Series, execution_price: str) -> float:
    """Return the configured execution price for a single OHLCV bar."""
    column = _EXECUTION_COLUMN.get(execution_price)
    if column is None:
        raise ValueError(f"Unsupported execution price: {execution_price!r}")
    if column not in bar.index:
        raise ValueError(f"Execution column '{column}' not found in bar")
    return float(bar[column])


def execute_signal(
    portfolio: Portfolio,
    signal: Signal,
    execution_bar: pd.Series,
    settings: Settings,
) -> Trade | None:
    """
    Execute a signal on the next bar to avoid look-ahead bias.

    The signal is generated from data through bar t; this function fills
    the order using bar t+1 prices.
    """
    price = get_execution_price(execution_bar, settings.execution.price)

    if signal.action == SignalAction.BUY:
        trade = portfolio.execute_buy(
            price=price,
            commission_rate=settings.commission_rate,
            slippage_bps=settings.slippage_bps,
            date=execution_bar.name,
        )
        if trade:
            logger.debug(
                "BUY %d shares @ %.2f on %s",
                trade.quantity,
                trade.price,
                trade.date,
            )
        return trade

    if signal.action == SignalAction.SELL:
        trade = portfolio.execute_sell(
            price=price,
            commission_rate=settings.commission_rate,
            slippage_bps=settings.slippage_bps,
            date=execution_bar.name,
        )
        if trade:
            logger.debug(
                "SELL %d shares @ %.2f on %s",
                trade.quantity,
                trade.price,
                trade.date,
            )
        return trade

    return None
