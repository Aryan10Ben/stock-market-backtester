import json
import os
from datetime import date

import pandas as pd

# Local imports
from api.db import get_connection, get_price_data, save_price_data
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backtester.data.loader import load_market_data_from_frame
from backtester.engine.backtester import Backtester
from backtester.metrics.calculator import calculate_metrics
from backtester.strategy import create_strategy

import logging

logger = logging.getLogger("api.index")

# Initialize FastAPI app
app = FastAPI(title="Stock Backtester API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.environ.get("DATABASE_URL")

class StrategyParams(BaseModel):
    fast_window: int = Field(default=20, alias="fastWindow")
    slow_window: int = Field(default=50, alias="slowWindow")

    class Config:
        populate_by_name = True

class BacktestRequest(BaseModel):
    ticker: str
    start_date: date = Field(alias="startDate")
    end_date: date = Field(alias="endDate")
    strategy: StrategyParams
    initial_cash: float = Field(default=100000.0, alias="initialCash")
    commission_pct: float = Field(default=0.1, alias="commissionPct")
    slippage_bps: float = Field(default=5.0, alias="slippageBps")

    class Config:
        populate_by_name = True

@app.get("/api/health")
def health_check():
    return {"status": "ok", "db_connected": DATABASE_URL is not None}

def fetch_data_with_cache(ticker: str, start_date: date, end_date: date) -> tuple[pd.DataFrame, str]:
    """Check Neon DB, fallback to yfinance/stooq."""
    # 1. Check Neon DB
    from api.db import get_price_data, save_price_data
    df = get_price_data(ticker, start_date, end_date)
    if not df.empty and df.index.min().date() <= start_date and df.index.max().date() >= end_date:
        return df, "price_cache"
        
    # 2. Fetch using existing robust fetcher
    from backtester.data.fetcher import fetch_ohlcv
    try:
        df = fetch_ohlcv(ticker, start_date, end_date)
        # Determine source by catching the logs or assuming yfinance if no error
        source = "yfinance" 
    except Exception as e:
        logger.error(f"Data fetch failed for {ticker}: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to fetch data: {e}")

    # 3. Save to Neon DB
    if not df.empty:
        save_price_data(ticker, df, source)

    return df, source

@app.post("/api/backtest")
def run_backtest(req: BacktestRequest):
    try:
        # Fetch Data
        frame, source = fetch_data_with_cache(req.ticker.upper(), req.start_date, req.end_date)

        overrides = {
            "ticker": req.ticker.upper(),
            "start_date": req.start_date,
            "end_date": req.end_date,
            "strategy": {
                "fast_window": req.strategy.fast_window,
                "slow_window": req.strategy.slow_window
            },
            "initial_cash": req.initial_cash,
            "commission_rate": req.commission_pct / 100.0,
            "slippage_bps": req.slippage_bps
        }

        # Initialize settings
        from backtester.config.loader import load_settings
        settings = load_settings(cli_overrides=overrides)

        # Run pipeline
        frame = load_market_data_from_frame(frame, min_bars=settings.min_required_bars, ticker=settings.ticker)
        strategy = create_strategy(settings)
        engine = Backtester(settings, strategy)
        result = engine.run(frame)
        calculate_metrics(result, settings)
        result.price_data = strategy.get_indicator_columns(frame)

        # Serialize
        equity_curve = [
            {
                "date": eq.date.isoformat(),
                "cash": eq.cash,
                "holdingsValue": eq.holdings_value,
                "totalValue": eq.total_value,
                "benchmarkValue": eq.benchmark_value
            }
            for eq in result.equity_curve
        ] if result.equity_curve else []

        signals = [
            {
                "date": s.date.isoformat(),
                "action": s.action.value,
                "price": s.price
            }
            for s in result.signals
        ] if result.signals else []

        trades = [
            {
                "date": t.date.isoformat(),
                "action": t.side.value,
                "quantity": t.quantity,
                "price": t.price,
                "cost": t.total_cost,
                "balanceAfter": t.portfolio_value_after
            }
            for t in result.trades
        ] if result.trades else []

        metrics = {}
        if result.metrics:
            m = result.metrics
            metrics = {
                "totalReturn": m.total_return,
                "cagr": m.cagr,
                "sharpeRatio": m.sharpe_ratio,
                "maxDrawdown": m.max_drawdown,
                "winRate": m.win_rate,
                "excessReturn": m.excess_return,
                "numTrades": m.num_trades
            }

        price_records = []
        if result.price_data is not None:
            df = result.price_data.copy()
            df.index = df.index.strftime('%Y-%m-%d')
            # Cast to object first so pandas allows inserting Python None instead of NaN
            df = df.astype(object).where(pd.notnull(df), None)
            price_records = df.reset_index().to_dict(orient="records")

        response = {
            "metrics": metrics,
            "equityCurve": equity_curve,
            "signals": signals,
            "trades": trades,
            "priceData": price_records,
            "dataSourceUsed": source
        }

        # Save History
        from api.db import save_run_to_db
        save_run_to_db(req.dict(by_alias=True), metrics)

        def clean_nans(obj):
            if isinstance(obj, dict):
                return {k: clean_nans(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_nans(v) for v in obj]
            elif isinstance(obj, float):
                import math
                if math.isnan(obj) or math.isinf(obj):
                    return None
            return obj

        return clean_nans(response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/history")
def get_history():
    from api.db import get_history_runs
    runs = get_history_runs()
    return {"runs": runs}
