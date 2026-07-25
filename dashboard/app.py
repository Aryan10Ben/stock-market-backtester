"""Main entry point for the Streamlit dashboard."""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root and src to PYTHONPATH so we can import from backtester and dashboard
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "src"))

import streamlit as st

from backtester.config.settings import Settings
from dashboard.components.charts import (
    render_drawdown_chart,
    render_equity_curve,
    render_price_chart,
)
from dashboard.components.controls import render_sidebar
from dashboard.components.summary import render_metrics_summary
from dashboard.components.trades_table import render_trades_table
from dashboard.services.backtest_service import run_dashboard_backtest
from dashboard.styles.theme import apply_theme, inject_custom_css

# Page Config must be the first Streamlit command
st.set_page_config(
    page_title="Stock Market Backtester",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global CSS and Plotly theme
inject_custom_css()
apply_theme()


def _render_strategy_profile(settings: Settings):
    """Render a compact strategy profile summary."""
    with st.expander("Strategy Profile", expanded=False):
        st.markdown(f"**Ticker:** {settings.ticker} | **Range:** {settings.start_date} to {settings.end_date}")
        st.markdown(f"**Parameters:** Fast MA ({settings.strategy.fast_window}), Slow MA ({settings.strategy.slow_window})")
        st.markdown(f"**Capital:** ${settings.initial_cash:,.2f} | **Fees:** Comm {settings.commission_rate * 100:.2f}%, Slip {settings.slippage_bps} bps")


def main():
    st.title("📈 Stock Market Backtester")
    st.markdown("A modular, high-performance backtesting engine.")

    # 1. Render Controls
    overrides, csv_frame, is_valid = render_sidebar()

    # 2. Run Button
    st.sidebar.markdown("---")
    run_clicked = st.sidebar.button("🚀 Run Backtest", type="primary", use_container_width=True, disabled=not is_valid)

    if run_clicked and is_valid:
        with st.spinner("Executing Backtest... (This might take a moment to fetch data)"):
            try:
                # 3. Execute Engine
                result, final_settings = run_dashboard_backtest(overrides, csv_frame)

                # 4. Render UI
                st.success(f"Backtest completed for **{final_settings.ticker}**")

                _render_strategy_profile(final_settings)

                if result.metrics:
                    render_metrics_summary(result)

                col1, col2 = st.columns([2, 1])
                with col1:
                    render_price_chart(result, final_settings)
                    render_equity_curve(result)
                with col2:
                    render_drawdown_chart(result)
                    render_trades_table(result)

            except Exception as e:
                # Friendlier error panel
                st.error("⚠️ **Data Fetch Failed**")
                st.markdown(f"*{str(e)}*")
                st.info("💡 **Tip:** Try using the 'Sample Tickers' from the sidebar, or upload a CSV file.")
    elif not run_clicked:
        st.info("👈 Configure parameters in the sidebar and click **Run Backtest**.")
    else:
        st.warning("Please fix the validation errors in the sidebar.")

if __name__ == "__main__":
    main()
