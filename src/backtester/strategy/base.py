"""Strategy base class."""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from backtester.models.core import Signal


class Strategy(ABC):
    """Abstract base for all trading strategies."""

    @abstractmethod
    def generate_signals(self, bars: pd.DataFrame) -> list[Signal]:
        """Generate trading signals from OHLCV bars.

        Must not use future data: signal at bar t uses only bars[0:t].
        """

    @abstractmethod
    def get_indicator_columns(self, bars: pd.DataFrame) -> pd.DataFrame:
        """Return bars with strategy indicator columns added (for charting)."""
