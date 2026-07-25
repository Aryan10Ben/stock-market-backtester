"""Trading strategy implementations."""

from backtester.strategy.base import Strategy
from backtester.strategy.factory import create_strategy
from backtester.strategy.ma_crossover import MovingAverageCrossover

__all__ = ["MovingAverageCrossover", "Strategy", "create_strategy"]
