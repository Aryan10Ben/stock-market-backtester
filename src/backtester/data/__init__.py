"""Data fetching, validation, cleaning, and caching."""

from backtester.data.loader import load_market_data, load_market_data_from_frame

__all__ = ["load_market_data", "load_market_data_from_frame"]
