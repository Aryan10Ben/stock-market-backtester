"""Tests for performance metrics."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import pytest

from backtester.config.loader import load_settings
from backtester.metrics.calculator import calculate_metrics
from backtester.models.core import Trade, TradeSide
from backtester.models.result import BacktestResult, EquityPoint


def _equity_curve(
    values: list[float],
    start: str = "2020-01-02",
    benchmark_values: list[float] | None = None,
) -> list[EquityPoint]:
    dates = pd.bdate_range(start, periods=len(values))
    bench = benchmark_values if benchmark_values is not None else values
    return [
        EquityPoint(
            date=dates[i],
            cash=values[i],
            holdings_value=0.0,
            total_value=values[i],
            benchmark_value=bench[i],
        )
        for i in range(len(values))
    ]


def _round_trip_trades(
    buy_price: float,
    sell_price: float,
    quantity: int = 100,
) -> list[Trade]:
    commission_rate = 0.001
    buy_gross = quantity * buy_price
    buy = Trade(
        date=datetime(2020, 1, 2),
        side=TradeSide.BUY,
        quantity=quantity,
        price=buy_price,
        commission=buy_gross * commission_rate,
        slippage_cost=0.0,
        portfolio_value_after=0.0,
    )
    sell_gross = quantity * sell_price
    sell = Trade(
        date=datetime(2020, 2, 1),
        side=TradeSide.SELL,
        quantity=quantity,
        price=sell_price,
        commission=sell_gross * commission_rate,
        slippage_cost=0.0,
        portfolio_value_after=0.0,
    )
    return [buy, sell]


@pytest.fixture
def settings(default_config_path):
    return load_settings(default_config_path)


def test_total_return_and_buy_and_hold(settings):
    curve = _equity_curve([100_000.0, 110_000.0, 120_000.0])
    result = BacktestResult(
        ticker="TEST",
        start_date=curve[0].date,
        end_date=curve[-1].date,
        equity_curve=curve,
    )
    metrics = calculate_metrics(result, settings)

    assert metrics.total_return == pytest.approx(0.2)
    assert metrics.buy_and_hold_return == pytest.approx(0.2)
    assert metrics.excess_return == pytest.approx(0.0)
    assert metrics.final_value == 120_000.0


def test_excess_return_vs_benchmark(settings):
    curve = _equity_curve(
        [100_000.0, 110_000.0, 130_000.0],
        benchmark_values=[100_000.0, 105_000.0, 120_000.0],
    )
    result = BacktestResult(
        ticker="TEST",
        start_date=curve[0].date,
        end_date=curve[-1].date,
        equity_curve=curve,
    )
    metrics = calculate_metrics(result, settings)
    assert metrics.total_return == pytest.approx(0.3)
    assert metrics.buy_and_hold_return == pytest.approx(0.2)
    assert metrics.excess_return == pytest.approx(0.1)


def test_max_drawdown(settings):
    curve = _equity_curve([100_000.0, 110_000.0, 99_000.0, 105_000.0])
    result = BacktestResult(
        ticker="TEST",
        start_date=curve[0].date,
        end_date=curve[-1].date,
        equity_curve=curve,
    )
    metrics = calculate_metrics(result, settings)
    assert metrics.max_drawdown == pytest.approx(-0.10, rel=1e-3)


def test_win_rate_winning_round_trip(settings):
    trades = _round_trip_trades(buy_price=100.0, sell_price=120.0)
    curve = _equity_curve([100_000.0, 102_000.0])
    result = BacktestResult(
        ticker="TEST",
        start_date=curve[0].date,
        end_date=curve[-1].date,
        trades=trades,
        equity_curve=curve,
    )
    metrics = calculate_metrics(result, settings)
    assert metrics.num_trades == 1
    assert metrics.num_winning_trades == 1
    assert metrics.num_losing_trades == 0
    assert metrics.win_rate == pytest.approx(1.0)


def test_win_rate_losing_round_trip(settings):
    trades = _round_trip_trades(buy_price=100.0, sell_price=80.0)
    curve = _equity_curve([100_000.0, 98_000.0])
    result = BacktestResult(
        ticker="TEST",
        start_date=curve[0].date,
        end_date=curve[-1].date,
        trades=trades,
        equity_curve=curve,
    )
    metrics = calculate_metrics(result, settings)
    assert metrics.num_trades == 1
    assert metrics.num_losing_trades == 1
    assert metrics.win_rate == pytest.approx(0.0)


def test_cagr_positive(settings):
    # Span ~2 business days is too short for meaningful CAGR — use wider range
    wide_dates = pd.bdate_range("2020-01-02", periods=504)  # ~2 years of business days
    start_val = 100_000.0
    end_val = 121_000.0
    wide_curve = [
        EquityPoint(
            date=wide_dates[i],
            cash=start_val + (end_val - start_val) * i / (len(wide_dates) - 1),
            holdings_value=0.0,
            total_value=start_val + (end_val - start_val) * i / (len(wide_dates) - 1),
            benchmark_value=start_val,
        )
        for i in range(len(wide_dates))
    ]
    result = BacktestResult(
        ticker="TEST",
        start_date=wide_dates[0],
        end_date=wide_dates[-1],
        equity_curve=wide_curve,
    )
    metrics = calculate_metrics(result, settings)
    assert metrics.cagr == pytest.approx(0.10, rel=0.05)


def test_sharpe_zero_on_flat_equity(settings):
    curve = _equity_curve([100_000.0] * 10)
    result = BacktestResult(
        ticker="TEST",
        start_date=curve[0].date,
        end_date=curve[-1].date,
        equity_curve=curve,
    )
    metrics = calculate_metrics(result, settings)
    assert metrics.sharpe_ratio == 0.0


def test_metrics_attached_to_result(settings):
    curve = _equity_curve([100_000.0, 105_000.0])
    result = BacktestResult(
        ticker="TEST",
        start_date=curve[0].date,
        end_date=curve[-1].date,
        equity_curve=curve,
    )
    returned = calculate_metrics(result, settings)
    assert result.metrics is returned
    assert result.metrics.excess_return == returned.excess_return


def test_empty_equity_curve_raises(settings):
    result = BacktestResult(
        ticker="TEST",
        start_date=datetime(2020, 1, 1),
        end_date=datetime(2020, 12, 31),
        equity_curve=[],
    )
    with pytest.raises(ValueError, match="equity curve"):
        calculate_metrics(result, settings)
