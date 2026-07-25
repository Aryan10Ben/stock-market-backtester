"""Tests for MA crossover strategy."""

from __future__ import annotations

import pytest

from backtester.config.settings import StrategySettings
from backtester.models.core import SignalAction
from backtester.strategy.factory import create_strategy
from backtester.strategy.ma_crossover import MovingAverageCrossover
from backtester.utils.exceptions import ConfigError


def test_generates_one_signal_per_bar(sample_bars, fast_strategy_config):
    strategy = MovingAverageCrossover(fast_window=fast_strategy_config.fast_window, slow_window=fast_strategy_config.slow_window, signal_on=fast_strategy_config.signal_on)
    signals = strategy.generate_signals(sample_bars)
    assert len(signals) == len(sample_bars)


def test_hold_during_warmup(sample_bars, fast_strategy_config):
    strategy = MovingAverageCrossover(fast_window=fast_strategy_config.fast_window, slow_window=fast_strategy_config.slow_window, signal_on=fast_strategy_config.signal_on)
    signals = strategy.generate_signals(sample_bars)
    slow = fast_strategy_config.slow_window
    warmup = signals[:slow]
    assert all(s.action == SignalAction.HOLD for s in warmup)


def test_detects_buy_and_sell_crossovers(crossover_bars, crossover_config):
    strategy = MovingAverageCrossover(fast_window=crossover_config.fast_window, slow_window=crossover_config.slow_window, signal_on=crossover_config.signal_on)
    signals = strategy.generate_signals(crossover_bars)
    buys = [s for s in signals if s.action == SignalAction.BUY]
    sells = [s for s in signals if s.action == SignalAction.SELL]
    assert len(buys) >= 1
    assert len(sells) >= 1
    assert buys[0].date < sells[0].date


def test_no_look_ahead_bias(sample_bars, fast_strategy_config):
    """Signals at bar t must not change when future bars are appended."""
    strategy = MovingAverageCrossover(fast_window=fast_strategy_config.fast_window, slow_window=fast_strategy_config.slow_window, signal_on=fast_strategy_config.signal_on)
    cutoff = 40

    full_signals = strategy.generate_signals(sample_bars)
    partial_signals = strategy.generate_signals(sample_bars.iloc[:cutoff])

    for i in range(cutoff):
        assert full_signals[i].action == partial_signals[i].action
        assert full_signals[i].price == partial_signals[i].price


def test_signals_use_only_past_data(crossover_bars, fast_strategy_config):
    """Truncating the series must not alter earlier crossover detection."""
    strategy = MovingAverageCrossover(fast_window=fast_strategy_config.fast_window, slow_window=fast_strategy_config.slow_window, signal_on=fast_strategy_config.signal_on)
    mid = 35

    early = strategy.generate_signals(crossover_bars.iloc[:mid])
    full = strategy.generate_signals(crossover_bars)

    early_buys = [i for i, s in enumerate(early) if s.action == SignalAction.BUY]
    full_buys = [i for i, s in enumerate(full[:mid]) if s.action == SignalAction.BUY]
    assert early_buys == full_buys


def test_indicator_columns_added(sample_bars, fast_strategy_config):
    strategy = MovingAverageCrossover(fast_window=fast_strategy_config.fast_window, slow_window=fast_strategy_config.slow_window, signal_on=fast_strategy_config.signal_on)
    enriched = strategy.get_indicator_columns(sample_bars)
    assert f"MA_{fast_strategy_config.fast_window}" in enriched.columns
    assert f"MA_{fast_strategy_config.slow_window}" in enriched.columns
    assert len(enriched) == len(sample_bars)


def test_missing_price_column_raises(sample_bars, fast_strategy_config):
    strategy = MovingAverageCrossover(fast_window=5, slow_window=20, signal_on="open")
    bad_bars = sample_bars.drop(columns=["Open"])
    with pytest.raises(ValueError, match="Open"):
        strategy.generate_signals(bad_bars)


def test_factory_creates_ma_crossover(default_settings):
    strategy = create_strategy(default_settings)
    assert isinstance(strategy, MovingAverageCrossover)


def test_factory_unknown_strategy_raises():
    config = StrategySettings.model_construct(name="invalid_strat", fast_window=5, slow_window=20)
    with pytest.raises(ConfigError, match="Unknown strategy"):
        create_strategy(config)


def test_buy_signal_has_reason(crossover_bars, crossover_config):
    strategy = MovingAverageCrossover(fast_window=crossover_config.fast_window, slow_window=crossover_config.slow_window, signal_on=crossover_config.signal_on)
    signals = strategy.generate_signals(crossover_bars)
    buys = [s for s in signals if s.action == SignalAction.BUY]
    assert len(buys) >= 1
    assert buys[0].reason != ""
    assert "crossed above" in buys[0].reason
