from __future__ import annotations

import pandas as pd

from backtester.models.core import Signal, SignalAction
from backtester.strategy.base import Strategy


class BollingerBandsStrategy(Strategy):
    """Bollinger Bands Volatility Breakout/Reversion Strategy.
    
    Buys when price crosses below the lower band.
    Sells when price crosses above the upper band.
    """

    def __init__(self, period: int = 20, num_std: float = 2.0):
        self.period = period
        self.num_std = num_std

    def _calculate_bands(self, bars: pd.DataFrame) -> pd.DataFrame:
        df = pd.DataFrame(index=bars.index)

        df["SMA"] = bars["Close"].rolling(window=self.period).mean()
        df["STD"] = bars["Close"].rolling(window=self.period).std()

        df["Upper_Band"] = df["SMA"] + (df["STD"] * self.num_std)
        df["Lower_Band"] = df["SMA"] - (df["STD"] * self.num_std)
        return df

    def generate_signals(self, bars: pd.DataFrame) -> list[Signal]:
        signals = []

        bands_df = self._calculate_bands(bars)

        holding = False
        for i in range(len(bars)):
            curr_price = bars.iloc[i]["Close"]
            date_str = bars.index[i].strftime("%Y-%m-%d")
            price = float(curr_price)
            action = SignalAction.HOLD

            if i == 0 or pd.isna(bands_df.iloc[i]["Lower_Band"]):
                signals.append(Signal(date=date_str, action=action, price=price))
                continue

            prev_price = bars.iloc[i-1]["Close"]
            curr_lower = bands_df.iloc[i]["Lower_Band"]
            curr_upper = bands_df.iloc[i]["Upper_Band"]
            prev_lower = bands_df.iloc[i-1]["Lower_Band"]
            prev_upper = bands_df.iloc[i-1]["Upper_Band"]

            # Cross below lower band -> BUY
            if prev_price >= prev_lower and curr_price < curr_lower and not holding:
                action = SignalAction.BUY
                holding = True

            # Cross above upper band -> SELL
            elif prev_price <= prev_upper and curr_price > curr_upper and holding:
                action = SignalAction.SELL
                holding = False

            signals.append(Signal(date=date_str, action=action, price=price))

        return signals

    def get_indicator_columns(self, bars: pd.DataFrame) -> pd.DataFrame:
        df = bars.copy()
        bands_df = self._calculate_bands(bars)
        df["BB_Upper"] = bands_df["Upper_Band"]
        df["BB_Lower"] = bands_df["Lower_Band"]
        df["BB_SMA"] = bands_df["SMA"]
        return df
