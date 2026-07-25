"""Sidebar controls for configuring and launching a backtest."""

from __future__ import annotations

import datetime
from typing import Any, Optional

import pandas as pd
import streamlit as st


def render_sidebar() -> tuple[dict[str, Any], Optional[pd.DataFrame], bool]:
    """Render the configuration controls in the sidebar and return settings overrides, csv, and validity."""
    st.sidebar.header("⚙️ Configuration")

    overrides = {}
    csv_frame = None
    is_valid = True

    # 1. Data Source
    st.sidebar.subheader("Data Source")
    data_mode = st.sidebar.radio(
        "Mode",
        ["Sample Tickers", "Custom Ticker", "CSV Upload"],
        horizontal=True,
        help="Select where to source historical data."
    )

    if data_mode == "Sample Tickers":
        ticker = st.sidebar.selectbox("Select a Sample", ["AAPL", "MSFT", "NVDA", "TSLA", "SPY"])
        overrides["ticker"] = ticker
    elif data_mode == "Custom Ticker":
        ticker = st.sidebar.text_input("Ticker Symbol", value="META", placeholder="e.g. META, AMZN, GOOG")
        if not ticker.strip():
            st.sidebar.error("Ticker symbol is required.")
            is_valid = False
        overrides["ticker"] = ticker.strip().upper()
    else:
        st.sidebar.info("Upload an OHLCV CSV file (Date, Open, High, Low, Close, Volume).")
        uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
        if uploaded_file is not None:
            try:
                csv_frame = pd.read_csv(uploaded_file, parse_dates=["Date"], index_col="Date")
                overrides["ticker"] = "CUSTOM"
            except Exception as e:
                st.sidebar.error(f"Failed to parse CSV: {e}")
                is_valid = False
        else:
            is_valid = False

    st.sidebar.divider()

    # 2. Date Range
    st.sidebar.subheader("Date Range")
    col1, col2 = st.sidebar.columns(2)
    start_date = col1.date_input("Start Date", datetime.date(2023, 1, 1))
    end_date = col2.date_input("End Date", datetime.date(2023, 12, 31))

    if start_date >= end_date:
        st.sidebar.error("Start Date must be before End Date.")
        is_valid = False

    overrides["start_date"] = start_date
    overrides["end_date"] = end_date

    st.sidebar.divider()

    # 3. Strategy Parameters
    st.sidebar.subheader("Strategy: MA Crossover")
    scol1, scol2 = st.sidebar.columns(2)
    fast_ma = scol1.number_input("Fast MA", min_value=2, max_value=200, value=20)
    slow_ma = scol2.number_input("Slow MA", min_value=3, max_value=500, value=50)

    if fast_ma >= slow_ma:
        st.sidebar.error("Fast MA must be less than Slow MA.")
        is_valid = False

    overrides["strategy"] = {
        "fast_window": fast_ma,
        "slow_window": slow_ma
    }

    # 4. Advanced Engine Settings
    with st.sidebar.expander("Advanced Settings (Capital & Fees)"):
        cash = st.number_input("Initial Cash ($)", min_value=1000, value=100000, step=5000)
        comm = st.number_input("Commission (%)", min_value=0.0, value=0.1, step=0.05, help="Brokerage commission per trade.")
        slip = st.number_input("Slippage (bps)", min_value=0.0, value=5.0, step=1.0, help="Slippage in basis points.")

        overrides["initial_cash"] = cash
        overrides["commission_rate"] = comm / 100.0
        overrides["slippage_bps"] = slip

    return overrides, csv_frame, is_valid
