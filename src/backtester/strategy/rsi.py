from __future__ import annotations

import pandas as pd

from backtester.models.core import Signal, SignalAction
from backtester.strategy.base import Strategy


class RSIStrategy(Strategy):
    """RSI Mean Reversion Strategy.
    
    Buys when RSI crosses below oversold_threshold (e.g. 30).
    Sells when RSI crosses above overbought_threshold (e.g. 70).
    """

    def __init__(self, period: int = 14, overbought: float = 70.0, oversold: float = 30.0):
        self.period = period
        self.overbought = overbought
        self.oversold = oversold

    def _calculate_rsi(self, bars: pd.DataFrame) -> pd.Series:
        delta = bars["Close"].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)

        avg_gain = gain.ewm(alpha=1/self.period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/self.period, adjust=False).mean()

        rs = avg_gain / avg_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))
        return rsi

    def generate_signals(self, bars: pd.DataFrame) -> list[Signal]:
        signals = []
        rsi = self._calculate_rsi(bars)

        holding = False
        for i in range(len(bars)):
            date_str = bars.index[i].strftime("%Y-%m-%d")
            price = float(bars.iloc[i]["Close"])
            action = SignalAction.HOLD

            curr_rsi = rsi.iloc[i]
            if i == 0 or pd.isna(curr_rsi):
                signals.append(Signal(date=date_str, action=action, price=price))
                continue

            prev_rsi = rsi.iloc[i-1]
            if pd.isna(prev_rsi):
                signals.append(Signal(date=date_str, action=action, price=price))
                continue

            # Cross below oversold
            if prev_rsi >= self.oversold and curr_rsi < self.oversold and not holding:
                action = SignalAction.BUY
                holding = True

            # Cross above overbought
            elif prev_rsi <= self.overbought and curr_rsi > self.overbought and holding:
                action = SignalAction.SELL
                holding = False

            signals.append(Signal(date=date_str, action=action, price=price))

        return signals

    def get_indicator_columns(self, bars: pd.DataFrame) -> pd.DataFrame:
        df = bars.copy()
        df["RSI"] = self._calculate_rsi(bars)
        df["Overbought"] = self.overbought
        df["Oversold"] = self.oversold
        return df
