"""Moving average crossover strategy."""

from __future__ import annotations

import logging

import pandas as pd

from backtester.models.core import Signal, SignalAction
from backtester.strategy.base import Strategy

logger = logging.getLogger("backtester.strategy.ma_crossover")

# Map config signal_on values to yfinance column names.
_PRICE_COLUMN_MAP = {
    "open": "Open",
    "high": "High",
    "low": "Low",
    "close": "Close",
}


class MovingAverageCrossover(Strategy):
    """
    Buy when the fast MA crosses above the slow MA; sell on cross below.

    Look-ahead prevention:
    - MAs at bar t use prices from bars [t - window + 1, t] only.
    - A crossover at bar t compares MA values at t and t-1.
    - The backtest engine executes these signals on bar t+1 (not here).
    """

    def __init__(self, fast_window: int = 20, slow_window: int = 50, signal_on: str = "close") -> None:
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.signal_on = signal_on
        self._price_col = _PRICE_COLUMN_MAP.get(signal_on, "Close")

    @property
    def name(self) -> str:
        return "ma_crossover"

    def generate_signals(self, bars: pd.DataFrame) -> list[Signal]:
        if self._price_col not in bars.columns:
            raise ValueError(f"Price column '{self._price_col}' not found in bars")

        prices = bars[self._price_col]
        fast_ma = prices.rolling(window=self.fast_window).mean()
        slow_ma = prices.rolling(window=self.slow_window).mean()

        signals: list[Signal] = []
        prev_diff: float | None = None

        for i in range(len(bars)):
            bar_date = bars.index[i]
            fast_val = fast_ma.iloc[i]
            slow_val = slow_ma.iloc[i]
            price = float(prices.iloc[i])

            if pd.isna(fast_val) or pd.isna(slow_val):
                signals.append(Signal(date=bar_date, action=SignalAction.HOLD, price=price))
                continue

            diff = float(fast_val - slow_val)
            action = SignalAction.HOLD
            reason = ""

            if prev_diff is not None:
                if prev_diff <= 0 < diff:
                    action = SignalAction.BUY
                    reason = (
                        f"Fast MA ({self.fast_window}) crossed above "
                        f"slow MA ({self.slow_window})"
                    )
                elif prev_diff >= 0 > diff:
                    action = SignalAction.SELL
                    reason = (
                        f"Fast MA ({self.fast_window}) crossed below "
                        f"slow MA ({self.slow_window})"
                    )

            signals.append(
                Signal(date=bar_date, action=action, price=price, reason=reason)
            )
            prev_diff = diff

        buy_count = sum(1 for s in signals if s.action == SignalAction.BUY)
        sell_count = sum(1 for s in signals if s.action == SignalAction.SELL)
        logger.info("Generated %d BUY and %d SELL signals", buy_count, sell_count)
        return signals

    def get_indicator_columns(self, bars: pd.DataFrame) -> pd.DataFrame:
        """Return bars with fast/slow MA columns added for charting."""
        result = bars.copy()
        price_col = self._price_col
        result[f"MA_{self.fast_window}"] = (
            result[price_col].rolling(window=self.fast_window).mean()
        )
        result[f"MA_{self.slow_window}"] = (
            result[price_col].rolling(window=self.slow_window).mean()
        )
        return result

