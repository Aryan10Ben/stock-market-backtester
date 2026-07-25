"""Tests for backtesting engine."""

from __future__ import annotations

import pandas as pd
import pytest

from backtester.config.loader import load_settings
from backtester.config.settings import ExecutionSettings, StrategySettings
from backtester.engine.backtester import Backtester
from backtester.strategy.ma_crossover import MovingAverageCrossover
from backtester.utils.exceptions import BacktestError


@pytest.fixture
def backtest_settings(default_config_path, crossover_config):
    settings = load_settings(default_config_path)
    return settings.model_copy(
        update={
            "ticker": "TEST",
            "initial_cash": 100_000.0,
            "strategy": crossover_config,
            "execution": ExecutionSettings(price="open"),
        }
    )


def test_backtest_runs(crossover_bars, backtest_settings):
    strategy = MovingAverageCrossover(fast_window=backtest_settings.strategy.fast_window, slow_window=backtest_settings.strategy.slow_window, signal_on=backtest_settings.strategy.signal_on)
    engine = Backtester(backtest_settings, strategy)
    result = engine.run(crossover_bars)

    assert len(result.equity_curve) == len(crossover_bars)
    assert result.equity_curve[0].total_value == backtest_settings.initial_cash
    assert result.ticker == "TEST"
    assert len(result.trades) >= 2


def test_backtest_is_deterministic(crossover_bars, backtest_settings):
    strategy = MovingAverageCrossover(fast_window=backtest_settings.strategy.fast_window, slow_window=backtest_settings.strategy.slow_window, signal_on=backtest_settings.strategy.signal_on)
    engine = Backtester(backtest_settings, strategy)

    result_a = engine.run(crossover_bars)
    result_b = engine.run(crossover_bars)

    assert len(result_a.trades) == len(result_b.trades)
    assert result_a.equity_curve[-1].total_value == result_b.equity_curve[-1].total_value
    for ta, tb in zip(result_a.trades, result_b.trades):
        assert ta.quantity == tb.quantity
        assert ta.price == tb.price


def test_next_bar_execution(crossover_bars, backtest_settings):
    """Trades must fill at bar t+1 open, not bar t close."""
    strategy = MovingAverageCrossover(fast_window=backtest_settings.strategy.fast_window, slow_window=backtest_settings.strategy.slow_window, signal_on=backtest_settings.strategy.signal_on)
    engine = Backtester(backtest_settings, strategy)

    bars = crossover_bars.copy()
    preview_signals = strategy.generate_signals(bars)
    first_buy_idx = next(
        i for i, s in enumerate(preview_signals) if s.action.value == "BUY"
    )
    exec_idx = first_buy_idx + 1
    bars.iloc[exec_idx, bars.columns.get_loc("Open")] = 999.0

    result = engine.run(bars)
    buys = [t for t in result.trades if t.side.value == "BUY"]
    assert len(buys) >= 1
    assert buys[0].price > 900.0


def test_last_signal_not_executed_without_next_bar(backtest_settings):
    """A signal on the final bar cannot execute."""
    dates = pd.bdate_range("2023-01-03", periods=25)
    close = [50.0] * 10 + list(range(60, 75))
    bars = pd.DataFrame(
        {
            "Open": close,
            "High": [c + 1 for c in close],
            "Low": [c - 1 for c in close],
            "Close": close,
            "Volume": 1_000_000.0,
        },
        index=dates,
    )
    config = StrategySettings(fast_window=3, slow_window=8, signal_on="close")
    settings = backtest_settings.model_copy(update={"strategy": config})
    strategy = MovingAverageCrossover(fast_window=config.fast_window, slow_window=config.slow_window, signal_on=config.signal_on)
    result = Backtester(settings, strategy).run(bars)

    # Even if last bar has a signal, no trade can occur without bar N+1.
    if result.signals and result.signals[-1].date == bars.index[-1]:
        assert all(t.date != bars.index[-1] for t in result.trades)


def test_empty_bars_raises(backtest_settings):
    strategy = MovingAverageCrossover(fast_window=backtest_settings.strategy.fast_window, slow_window=backtest_settings.strategy.slow_window, signal_on=backtest_settings.strategy.signal_on)
    engine = Backtester(backtest_settings, strategy)
    with pytest.raises(BacktestError, match="empty"):
        engine.run(pd.DataFrame())
