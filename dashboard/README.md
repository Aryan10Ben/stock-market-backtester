# Backtester Web Dashboard

A professional, local web dashboard for the Stock Market Backtesting System built with Streamlit and Plotly.

## Quick Start

1. Install dashboard dependencies:
   ```bash
   pip install -e .
   ```
   (Make sure you're in the project root so it reads `pyproject.toml` which includes `streamlit` and `plotly`).

2. Launch the dashboard:
   ```bash
   streamlit run dashboard/app.py
   ```

## Features

- **Zero-config integration**: Connects directly to the existing Python engine without needing REST APIs.
- **Interactive UI**: Fetch from Yahoo Finance or upload local OHLCV CSVs directly in the sidebar.
- **Rich Visuals**: Plotly-powered interactive candlestick charts, equity curves, and drawdown charts.
- **Safe**: Completely respects the underlying engine's validation and error handling logic.
