from __future__ import annotations

import pandas as pd

from backtester.models.core import Signal, SignalAction
from backtester.strategy.base import Strategy


class MACDStrategy(Strategy):
    """MACD Trend Following Strategy.
    
    Buys when MACD crosses above Signal Line.
    Sells when MACD crosses below Signal Line.
    """

    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    def _calculate_macd(self, bars: pd.DataFrame) -> pd.DataFrame:
        df = pd.DataFrame(index=bars.index)

        # Calculate EMAs
        ema_fast = bars["Close"].ewm(span=self.fast_period, adjust=False).mean()
        ema_slow = bars["Close"].ewm(span=self.slow_period, adjust=False).mean()

        # MACD Line
        df["MACD"] = ema_fast - ema_slow

        # Signal Line
        df["Signal_Line"] = df["MACD"].ewm(span=self.signal_period, adjust=False).mean()

        # Histogram
        df["MACD_Histogram"] = df["MACD"] - df["Signal_Line"]
        return df

    def generate_signals(self, bars: pd.DataFrame) -> list[Signal]:
        signals = []
        macd_df = self._calculate_macd(bars)

        holding = False
        for i in range(len(bars)):
            date_str = bars.index[i].strftime("%Y-%m-%d")
            price = float(bars.iloc[i]["Close"])
            action = SignalAction.HOLD

            curr_macd = macd_df.iloc[i]["MACD"]
            curr_signal = macd_df.iloc[i]["Signal_Line"]
            if i == 0 or pd.isna(curr_macd) or pd.isna(curr_signal):
                signals.append(Signal(date=date_str, action=action, price=price))
                continue

            prev_macd = macd_df.iloc[i-1]["MACD"]
            prev_signal = macd_df.iloc[i-1]["Signal_Line"]
            if pd.isna(prev_macd) or pd.isna(prev_signal):
                signals.append(Signal(date=date_str, action=action, price=price))
                continue

            # Cross above
            if prev_macd <= prev_signal and curr_macd > curr_signal and not holding:
                action = SignalAction.BUY
                holding = True

            # Cross below
            elif prev_macd >= prev_signal and curr_macd < curr_signal and holding:
                action = SignalAction.SELL
                holding = False

            signals.append(Signal(date=date_str, action=action, price=price))

        return signals

    def get_indicator_columns(self, bars: pd.DataFrame) -> pd.DataFrame:
        df = bars.copy()
        macd_df = self._calculate_macd(bars)
        df["MACD"] = macd_df["MACD"]
        df["Signal_Line"] = macd_df["Signal_Line"]
        df["MACD_Histogram"] = macd_df["MACD_Histogram"]
        return df
