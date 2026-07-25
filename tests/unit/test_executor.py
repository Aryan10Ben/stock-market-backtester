"""Tests for order execution."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import pytest

from backtester.config.loader import load_settings
from backtester.engine.executor import execute_signal, get_execution_price
from backtester.engine.portfolio import Portfolio
from backtester.models.core import Signal, SignalAction, TradeSide


@pytest.fixture
def settings(default_config_path):
    return load_settings(default_config_path)


def test_get_execution_price_open():
    bar = pd.Series({"Open": 101.0, "Close": 99.0}, name=datetime(2020, 1, 2))
    assert get_execution_price(bar, "open") == 101.0


def test_get_execution_price_close():
    bar = pd.Series({"Open": 101.0, "Close": 99.0}, name=datetime(2020, 1, 2))
    assert get_execution_price(bar, "close") == 99.0


def test_execute_buy_signal(settings):
    portfolio = Portfolio(cash=100_000.0)
    signal = Signal(date=datetime(2020, 1, 1), action=SignalAction.BUY, price=100.0)
    bar = pd.Series({"Open": 102.0, "Close": 103.0}, name=datetime(2020, 1, 2))

    trade = execute_signal(portfolio, signal, bar, settings)
    assert trade is not None
    assert trade.side == TradeSide.BUY
    assert portfolio.is_long


def test_execute_sell_signal(settings):
    portfolio = Portfolio(cash=100_000.0)
    buy_bar = pd.Series({"Open": 100.0, "Close": 100.0}, name=datetime(2020, 1, 2))
    buy_signal = Signal(date=datetime(2020, 1, 1), action=SignalAction.BUY, price=100.0)
    execute_signal(portfolio, buy_signal, buy_bar, settings)

    sell_signal = Signal(date=datetime(2020, 2, 1), action=SignalAction.SELL, price=110.0)
    sell_bar = pd.Series({"Open": 110.0, "Close": 111.0}, name=datetime(2020, 2, 2))
    trade = execute_signal(portfolio, sell_signal, sell_bar, settings)

    assert trade is not None
    assert trade.side == TradeSide.SELL
    assert not portfolio.is_long


def test_hold_signal_does_nothing(settings):
    portfolio = Portfolio(cash=100_000.0)
    signal = Signal(date=datetime(2020, 1, 1), action=SignalAction.HOLD, price=100.0)
    bar = pd.Series({"Open": 100.0, "Close": 100.0}, name=datetime(2020, 1, 2))
    assert execute_signal(portfolio, signal, bar, settings) is None
    assert not portfolio.is_long
