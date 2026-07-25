"""Tests for portfolio management."""

from __future__ import annotations

from datetime import datetime

from backtester.engine.portfolio import Portfolio
from backtester.models.core import TradeSide


def test_initial_state():
    portfolio = Portfolio(cash=100_000.0)
    assert portfolio.cash == 100_000.0
    assert portfolio.quantity == 0
    assert not portfolio.is_long
    assert portfolio.total_value(100.0) == 100_000.0


def test_buy_reduces_cash_and_opens_position():
    portfolio = Portfolio(cash=100_000.0)
    trade = portfolio.execute_buy(
        price=100.0,
        commission_rate=0.001,
        slippage_bps=5,
        date=datetime(2020, 1, 2),
    )
    assert trade is not None
    assert trade.side == TradeSide.BUY
    assert portfolio.is_long
    assert portfolio.cash < 100_000.0
    assert portfolio.quantity > 0
    assert trade.commission > 0
    assert trade.slippage_cost > 0


def test_buy_skipped_when_already_long():
    portfolio = Portfolio(cash=100_000.0)
    portfolio.execute_buy(
        price=100.0, commission_rate=0.001, slippage_bps=5, date=datetime(2020, 1, 2)
    )
    second = portfolio.execute_buy(
        price=100.0, commission_rate=0.001, slippage_bps=5, date=datetime(2020, 1, 3)
    )
    assert second is None
    assert len(portfolio.trades) == 1


def test_sell_closes_position():
    portfolio = Portfolio(cash=100_000.0)
    portfolio.execute_buy(
        price=100.0, commission_rate=0.001, slippage_bps=5, date=datetime(2020, 1, 2)
    )
    trade = portfolio.execute_sell(
        price=110.0, commission_rate=0.001, slippage_bps=5, date=datetime(2020, 2, 1)
    )
    assert trade is not None
    assert trade.side == TradeSide.SELL
    assert not portfolio.is_long
    assert portfolio.quantity == 0
    assert portfolio.cash > 100_000.0


def test_sell_skipped_when_flat():
    portfolio = Portfolio(cash=100_000.0)
    assert portfolio.execute_sell(
        price=100.0, commission_rate=0.001, slippage_bps=5, date=datetime(2020, 1, 2)
    ) is None


def test_integer_share_sizing():
    portfolio = Portfolio(cash=1_000.0)
    trade = portfolio.execute_buy(
        price=300.0, commission_rate=0.001, slippage_bps=0, date=datetime(2020, 1, 2)
    )
    assert trade is not None
    assert trade.quantity == 3  # floor(1000 / (300 * 1.001)) == 3
    assert isinstance(trade.quantity, int)
