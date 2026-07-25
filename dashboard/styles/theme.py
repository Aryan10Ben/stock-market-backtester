"""Design tokens and Plotly templates for a professional fintech aesthetic."""

import plotly.io as pio

# Color Palette (Dark Theme / Professional)
COLORS = {
    "background": "#0e1117",
    "card": "#1a1c24",
    "text_primary": "#f8f9fa",
    "text_secondary": "#a0a5b1",
    "primary": "#3b82f6",  # Blue (Portfolio)
    "success": "#10b981",  # Green (Gain/Buy)
    "danger": "#ef4444",   # Red (Loss/Sell/Drawdown)
    "warning": "#f59e0b",  # Amber
    "benchmark": "rgba(255,255,255,0.2)", # Muted Gray (Buy&Hold)
    "buy": "#10b981",
    "sell": "#ef4444",
    "equity": "#3b82f6",   # Blue
    "drawdown": "#ef4444", # Red
}

# Base layout for all Plotly charts
BASE_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, system-ui, sans-serif", color=COLORS["text_secondary"]),
    margin=dict(l=40, r=40, t=50, b=40),
    xaxis=dict(
        showgrid=False, # Removed vertical grids
        zeroline=False,
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.05)",
        zeroline=False,
    ),
    hovermode="x unified",
    hoverlabel=dict(
        bgcolor=COLORS["card"],
        font_size=12,
        font_family="Inter, system-ui, sans-serif"
    )
)

def apply_theme():
    """Register and set the custom Plotly template globally."""
    pio.templates["fintech_dark"] = pio.templates["plotly_dark"]
    pio.templates["fintech_dark"].layout.update(BASE_LAYOUT)
    pio.templates.default = "fintech_dark"

def inject_custom_css():
    """Inject custom CSS for UI polish (rounded cards, soft metrics)."""
    import streamlit as st
    st.markdown(
        """
        <style>
        /* Card styling for stMetric */
        div[data-testid="stMetric"] {
            background-color: #1a1c24;
            border-radius: 12px;
            padding: 16px 24px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        div[data-testid="stMetric"]:hover {
            border-color: rgba(255, 255, 255, 0.1);
            transition: 0.2s ease-in-out;
        }
        /* Metric Typography Hierarchy */
        div[data-testid="stMetricLabel"] {
            text-transform: uppercase;
            font-size: 13px !important;
            color: #a0a5b1 !important;
            font-weight: 500;
        }
        div[data-testid="stMetricValue"] {
            font-size: 28px !important;
            font-weight: 700 !important;
            color: #f8f9fa !important;
        }
        /* Make headings softer */
        h1, h2, h3 {
            color: #f8f9fa !important;
            font-weight: 500 !important;
        }
        /* Buttons */
        div.stButton > button {
            border-radius: 8px !important;
            font-weight: 500 !important;
        }
        /* Expanders */
        .streamlit-expanderHeader {
            border-radius: 8px !important;
        }
        /* Trade Table Action Colors */
        .trade-buy { color: #10b981; font-weight: bold; }
        .trade-sell { color: #ef4444; font-weight: bold; }
        </style>
        """,
        unsafe_allow_html=True
    )
