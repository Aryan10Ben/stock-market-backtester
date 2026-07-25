"""Portfolio state tracking."""

from __future__ import annotations

from dataclasses import dataclass, field

from backtester.models.core import Trade, TradeSide


@dataclass
class Portfolio:
    """Tracks cash, holdings, and executed trades during a backtest."""

    cash: float
    quantity: int = 0
    avg_cost: float = 0.0
    trades: list[Trade] = field(default_factory=list)

    @property
    def is_long(self) -> bool:
        return self.quantity > 0

    def holdings_value(self, price: float) -> float:
        return self.quantity * price

    def total_value(self, price: float) -> float:
        return self.cash + self.holdings_value(price)

    def execute_buy(
        self,
        price: float,
        commission_rate: float,
        slippage_bps: float,
        date,
    ) -> Trade | None:
        """Buy as many whole shares as cash allows. Long-only; skips if already long."""
        if self.is_long or self.cash <= 0:
            return None

        slip_multiplier = 1 + slippage_bps / 10_000
        exec_price = price * slip_multiplier

        # Integer shares: floor division after reserving commission headroom.
        max_shares = int(self.cash / (exec_price * (1 + commission_rate)))
        if max_shares <= 0:
            return None

        gross = max_shares * exec_price
        commission = gross * commission_rate
        slippage_cost = max_shares * (exec_price - price)
        total_cost = gross + commission

        self.cash -= total_cost
        self.quantity = max_shares
        self.avg_cost = exec_price

        trade = Trade(
            date=date,
            side=TradeSide.BUY,
            quantity=max_shares,
            price=exec_price,
            commission=commission,
            slippage_cost=slippage_cost,
            portfolio_value_after=self.total_value(price),
        )
        self.trades.append(trade)
        return trade

    def execute_sell(
        self,
        price: float,
        commission_rate: float,
        slippage_bps: float,
        date,
    ) -> Trade | None:
        """Sell entire position. Skips if flat."""
        if not self.is_long:
            return None

        slip_multiplier = 1 - slippage_bps / 10_000
        exec_price = price * slip_multiplier
        quantity = self.quantity
        gross = quantity * exec_price
        commission = gross * commission_rate
        slippage_cost = quantity * (price - exec_price)
        proceeds = gross - commission

        self.cash += proceeds
        self.quantity = 0
        self.avg_cost = 0.0

        trade = Trade(
            date=date,
            side=TradeSide.SELL,
            quantity=quantity,
            price=exec_price,
            commission=commission,
            slippage_cost=slippage_cost,
            portfolio_value_after=self.total_value(price),
        )
        self.trades.append(trade)
        return trade
