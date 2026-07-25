"""Strategy factory — instantiate strategies from configuration."""

from __future__ import annotations

from backtester.config.settings import Settings, StrategySettings
from backtester.strategy.base import Strategy
from backtester.strategy.bollinger import BollingerBandsStrategy
from backtester.strategy.buy_hold import BuyAndHoldStrategy
from backtester.strategy.ma_crossover import MovingAverageCrossover
from backtester.strategy.macd import MACDStrategy
from backtester.strategy.rsi import RSIStrategy
from backtester.utils.exceptions import ConfigError


def create_strategy(settings: Settings | StrategySettings) -> Strategy:
    """Create a strategy by configuration.
    
    Args:
        settings: The global settings or strategy settings object.
    """
    config = settings.strategy if isinstance(settings, Settings) else settings
    name = config.name

    if name == "ma_crossover":
        return MovingAverageCrossover(fast_window=config.fast_window, slow_window=config.slow_window)
    elif name == "rsi":
        return RSIStrategy(period=config.rsi_period, overbought=config.rsi_overbought, oversold=config.rsi_oversold)
    elif name == "macd":
        return MACDStrategy(fast_period=config.macd_fast, slow_period=config.macd_slow, signal_period=config.macd_signal)
    elif name == "bollinger":
        return BollingerBandsStrategy(period=config.bb_period, num_std=config.bb_std)
    elif name == "buy_hold":
        return BuyAndHoldStrategy()
    else:
        raise ConfigError(f"Unknown strategy: {name}")
