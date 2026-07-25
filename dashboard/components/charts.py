"""Interactive Plotly charts for the dashboard."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from backtester.config.settings import Settings
from backtester.models.core import SignalAction
from backtester.models.result import BacktestResult
from dashboard.styles.theme import COLORS


def render_price_chart(result: BacktestResult, settings: Settings) -> None:
    """Render candlestick chart with indicator overlays and signal markers."""
    st.markdown("### Price Action & Signals")

    df = result.price_data
    if df is None or df.empty:
        st.info("No price data available.")
        return

    fig = go.Figure()

    # 1. Candlesticks
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="Price",
        increasing_line_color=COLORS["success"],
        decreasing_line_color=COLORS["danger"]
    ))

    # 2. Indicator overlays — dynamically plot any non-OHLCV column
    base_cols = {"Open", "High", "Low", "Close", "Volume"}
    indicator_colors = [COLORS["warning"], COLORS["primary"], "#8b5cf6", "#ec4899", "#06b6d4"]
    indicator_cols = [c for c in df.columns if c not in base_cols]

    for i, col in enumerate(indicator_cols):
        color = indicator_colors[i % len(indicator_colors)]
        fig.add_trace(go.Scatter(
            x=df.index, y=df[col],
            line=dict(color=color, width=1.5),
            name=col
        ))

    # 3. Buy/Sell Signals
    buys = [s for s in result.signals if s.action == SignalAction.BUY]
    sells = [s for s in result.signals if s.action == SignalAction.SELL]

    if buys:
        fig.add_trace(go.Scatter(
            x=[b.date for b in buys],
            y=[b.price for b in buys],
            mode="markers",
            marker=dict(symbol="triangle-up", size=12, color=COLORS["buy"]),
            name="BUY"
        ))
    if sells:
        fig.add_trace(go.Scatter(
            x=[s.date for s in sells],
            y=[s.price for s in sells],
            mode="markers",
            marker=dict(symbol="triangle-down", size=12, color=COLORS["sell"]),
            name="SELL"
        ))

    fig.update_layout(height=500, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)


def render_equity_curve(result: BacktestResult) -> None:
    """Render the portfolio equity curve vs the benchmark."""
    st.markdown("### Portfolio Equity")

    if not result.equity_curve:
        return

    dates = [p.date for p in result.equity_curve]
    portfolio = [p.total_value for p in result.equity_curve]
    benchmark = [p.benchmark_value for p in result.equity_curve]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates, y=portfolio,
        line=dict(color=COLORS["equity"], width=2),
        name="Portfolio",
        fill="tozeroy",
        fillcolor="rgba(59, 130, 246, 0.1)" # primary blue opacity
    ))

    fig.add_trace(go.Scatter(
        x=dates, y=benchmark,
        line=dict(color=COLORS["benchmark"], width=2, dash="dash"),
        name="Buy & Hold"
    ))

    fig.update_layout(height=400, yaxis_tickformat="$,.0f")
    st.plotly_chart(fig, use_container_width=True, key=None)


def render_drawdown_chart(result: BacktestResult) -> None:
    """Render the underwater drawdown chart."""
    st.markdown("### Drawdown Profile")

    if not result.equity_curve:
        return

    # Calculate drawdown series
    df = pd.DataFrame({"value": [p.total_value for p in result.equity_curve]},
                      index=[p.date for p in result.equity_curve])

    df["peak"] = df["value"].cummax()
    df["drawdown"] = (df["value"] - df["peak"]) / df["peak"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, y=df["drawdown"],
        line=dict(color=COLORS["drawdown"], width=1),
        name="Drawdown",
        fill="tozeroy",
        fillcolor="rgba(239, 68, 68, 0.2)"
    ))

    fig.update_layout(height=300, yaxis_tickformat=".1%")
    st.plotly_chart(fig, use_container_width=True)
