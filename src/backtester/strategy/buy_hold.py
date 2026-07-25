from __future__ import annotations

import pandas as pd

from backtester.models.core import Signal, SignalAction
from backtester.strategy.base import Strategy


class BuyAndHoldStrategy(Strategy):
    """Buy on the first available bar and hold until the end."""

    def generate_signals(self, bars: pd.DataFrame) -> list[Signal]:
        signals = []
        for i in range(len(bars)):
            date_str = bars.index[i].strftime("%Y-%m-%d")
            price = float(bars.iloc[i]["Close"])
            action = SignalAction.BUY if i == 0 else SignalAction.HOLD
            signals.append(Signal(date=date_str, action=action, price=price))
        return signals

    def get_indicator_columns(self, bars: pd.DataFrame) -> pd.DataFrame:
        df = bars.copy()
        # No specific indicators for Buy and Hold
        return df
