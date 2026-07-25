"""KPI summary cards for backtest metrics."""

import streamlit as st

from backtester.models.result import BacktestResult


def render_metrics_summary(result: BacktestResult) -> None:
    """Render key performance indicators as metric cards."""
    metrics = result.metrics
    if not metrics:
        return

    st.markdown("### Performance Summary")

    # Check for open position at end of backtest
    if result.equity_curve and result.equity_curve[-1].portfolio_qty > 0:
        last_point = result.equity_curve[-1]
        open_qty = last_point.portfolio_qty

        # Calculate unrealized PnL: current value of holdings minus the cost basis
        # Cost basis is roughly (total value - cash). We know last_point.total_value and cash.
        # But wait, we can just say "Open Position: {qty} shares".
        st.info(f"📈 **1 Open Position:** Strategy holds {open_qty} shares at the end of the backtest window.")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        label="Total Return",
        value=f"{metrics.total_return * 100:.2f}%",
        delta=f"{metrics.excess_return * 100:.2f}% vs B&H"
    )

    col2.metric(
        label="CAGR",
        value=f"{metrics.cagr * 100:.2f}%"
    )

    col3.metric(
        label="Sharpe Ratio",
        value=f"{metrics.sharpe_ratio:.2f}"
    )

    col4.metric(
        label="Max Drawdown",
        value=f"{metrics.max_drawdown * 100:.2f}%",
        delta_color="inverse"
    )

    col5.metric(
        label="Win Rate",
        value=f"{metrics.win_rate * 100:.1f}%",
        help=f"{metrics.num_winning_trades}W / {metrics.num_losing_trades}L (Does not include open positions)"
    )

    st.markdown("---")
