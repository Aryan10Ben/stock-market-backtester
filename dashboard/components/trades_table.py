"""Trade log table component."""

import pandas as pd
import streamlit as st

from backtester.models.result import BacktestResult


def render_trades_table(result: BacktestResult) -> None:
    """Render a sortable, filterable dataframe of executed trades."""
    st.markdown("### Trade History")

    if not result.trades:
        st.info("No trades executed during this backtest.")
        return

    # Convert dataclasses to dicts for pandas
    trade_data = []
    for t in result.trades:
        trade_data.append({
            "Date": t.date.date(),
            "Action": t.side.value,
            "Quantity": t.quantity,
            "Price": float(t.price),
            "Cost/Revenue": t.total_cost,
            "Commission": t.commission,
            "Slippage": t.slippage_cost,
            "Balance After": t.portfolio_value_after
        })

    df = pd.DataFrame(trade_data)

    def color_action(val):
        if val == "BUY":
            return "color: #10b981; font-weight: bold;"
        elif val == "SELL":
            return "color: #ef4444; font-weight: bold;"
        return ""

    # Render with Streamlit's native dataframe viewer
    st.dataframe(
        df.style.applymap(color_action, subset=["Action"]) if hasattr(df.style, "applymap") else df.style.map(color_action, subset=["Action"]),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
            "Price": st.column_config.NumberColumn("Price", format="$%.2f"),
            "Cost/Revenue": st.column_config.NumberColumn("Total Cost", format="$%.2f"),
            "Commission": st.column_config.NumberColumn("Commission", format="$%.2f"),
            "Slippage": st.column_config.NumberColumn("Slippage", format="$%.2f"),
            "Balance After": st.column_config.NumberColumn("Balance", format="$%.2f"),
            "Action": st.column_config.TextColumn("Side"),
        }
    )
