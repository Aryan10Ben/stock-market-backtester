from datetime import date

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError

from backtester.config.settings import DataSettings, Settings, StrategySettings
from backtester.data.loader import load_market_data
from backtester.engine.backtester import Backtester
from backtester.metrics.calculator import calculate_metrics
from backtester.strategy import create_strategy
from backtester.utils.exceptions import (
    BacktesterError,
    BacktestError,
    ConfigError,
    DataFetchError,
    DataValidationError,
)

app = FastAPI(title="Stock Market Backtester API")

# Allow CORS for local frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BacktestRequest(BaseModel):
    ticker: str
    start_date: date
    end_date: date
    strategy: str = "ma_crossover"

    # MA Crossover
    fast_window: int = 20
    slow_window: int = 50

    # RSI
    rsi_period: int = 14
    rsi_overbought: float = 70.0
    rsi_oversold: float = 30.0

    # MACD
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9

    # Bollinger Bands
    bb_period: int = 20
    bb_std: float = 2.0

    # Portfolio
    initial_cash: float = 100000.0
    commission_rate: float = 0.001
    slippage_bps: float = 5.0

@app.post("/api/backtest")
def run_backtest(req: BacktestRequest):
    try:
        settings = Settings(
            ticker=req.ticker.upper(),
            start_date=req.start_date,
            end_date=req.end_date,
            initial_cash=req.initial_cash,
            commission_rate=req.commission_rate,
            slippage_bps=req.slippage_bps,
            strategy=StrategySettings(
                name=req.strategy,
                fast_window=req.fast_window,
                slow_window=req.slow_window,
                rsi_period=req.rsi_period,
                rsi_overbought=req.rsi_overbought,
                rsi_oversold=req.rsi_oversold,
                macd_fast=req.macd_fast,
                macd_slow=req.macd_slow,
                macd_signal=req.macd_signal,
                bb_period=req.bb_period,
                bb_std=req.bb_std
            ),
            data=DataSettings(cache_enabled=True)
        )

        # 1. Load Data
        bars = load_market_data(settings)

        # 2. Generate Signals
        strategy = create_strategy(settings)

        # 3. Execute Backtest
        engine = Backtester(settings, strategy)
        result = engine.run(bars)

        # Calculate metrics
        calculate_metrics(result, settings)

        # 4. Attach indicator columns for plotting
        result.price_data = strategy.get_indicator_columns(bars)

        # Format response
        equity_curve = [
            {
                "date": p.date.strftime("%Y-%m-%d"),
                "total_value": p.total_value,
                "benchmark_value": p.benchmark_value,
                "holdings_value": p.holdings_value,
                "portfolio_qty": p.portfolio_qty,
                "cash": p.cash
            } for p in result.equity_curve
        ]

        trades = [
            {
                "date": t.date.strftime("%Y-%m-%d"),
                "side": t.side.value,
                "quantity": t.quantity,
                "price": t.price,
                "commission": t.commission,
                "slippage_cost": t.slippage_cost,
                "total_cost": t.total_cost,
                "portfolio_value_after": t.portfolio_value_after
            } for t in result.trades
        ]

        # We need the price data + MA lines for charting
        import math

        price_records = []
        # Identify indicator columns (anything not OHLCV)
        base_cols = {"Open", "High", "Low", "Close", "Volume"}
        indicator_cols = [c for c in result.price_data.columns if c not in base_cols]

        for d, row in result.price_data.iterrows():
            record = {
                "time": d.strftime("%Y-%m-%d"),
                "open": None if math.isnan(row.get("Open", float('nan'))) else row.get("Open"),
                "high": None if math.isnan(row.get("High", float('nan'))) else row.get("High"),
                "low": None if math.isnan(row.get("Low", float('nan'))) else row.get("Low"),
                "close": None if math.isnan(row.get("Close", float('nan'))) else row.get("Close"),
                "volume": None if math.isnan(row.get("Volume", float('nan'))) else row.get("Volume"),
                "indicators": {}
            }

            for ind_col in indicator_cols:
                val = row[ind_col]
                record["indicators"][ind_col] = None if math.isnan(val) else val

            # Add signals
            signal = next((s for s in result.signals if s.date == d and s.action.name != "HOLD"), None)
            if signal:
                record["signal"] = signal.action.name

            price_records.append(record)

        metrics_dict = None
        if result.metrics:
            metrics_dict = {
                "total_return": result.metrics.total_return,
                "cagr": result.metrics.cagr,
                "max_drawdown": result.metrics.max_drawdown,
                "sharpe_ratio": result.metrics.sharpe_ratio,
                "win_rate": result.metrics.win_rate,
                "num_trades": result.metrics.num_trades,
                "num_winning_trades": result.metrics.num_winning_trades,
                "num_losing_trades": result.metrics.num_losing_trades,
                "excess_return": result.metrics.excess_return,
                "initial_cash": result.metrics.initial_cash,
                "final_value": result.metrics.final_value
            }

        return {
            "status": "success",
            "metrics": metrics_dict,
            "equity_curve": equity_curve,
            "trades": trades,
            "price_data": price_records,
            "settings": {
                "ticker": settings.ticker,
                "start_date": settings.start_date,
                "end_date": settings.end_date
            }
        }

    except DataValidationError as e:
        return JSONResponse(status_code=400, content={
            "success": False,
            "error_type": "data_error",
            "error_message": str(e),
            "troubleshooting": "Verify that the requested ticker has valid data for this date range. Try adjusting the dates or uploading a clean CSV."
        })
    except DataFetchError as e:
        return JSONResponse(status_code=400, content={
            "success": False,
            "error_type": "network_error",
            "error_message": str(e),
            "troubleshooting": "The data provider might be rate-limiting requests or the ticker is invalid. Try using a known ticker (AAPL) or use the CSV upload fallback."
        })
    except ValidationError as e:
        return JSONResponse(status_code=400, content={
            "success": False,
            "error_type": "input_error",
            "error_message": "Invalid parameters: " + str(e),
            "troubleshooting": "Check your strategy parameters. Ensure Fast MA is less than Slow MA, and capital/fees are positive."
        })
    except ConfigError as e:
        return JSONResponse(status_code=400, content={
            "success": False,
            "error_type": "input_error",
            "error_message": str(e),
            "troubleshooting": "Check your strategy parameters. Ensure Fast MA is less than Slow MA, and capital/fees are positive."
        })
    except BacktestError as e:
        return JSONResponse(status_code=400, content={
            "success": False,
            "error_type": "engine_error",
            "error_message": str(e),
            "troubleshooting": "The backtest engine encountered a runtime issue (e.g. division by zero, empty dataset). Please report this bug."
        })
    except BacktesterError as e:
        return JSONResponse(status_code=400, content={
            "success": False,
            "error_type": "unknown_error",
            "error_message": str(e),
            "troubleshooting": "An unexpected backtesting error occurred."
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "error_type": "system_error",
            "error_message": f"Internal error: {str(e)}",
            "troubleshooting": "The server crashed unexpectedly. Please check the backend logs."
        })

@app.get("/api/search")
def search_tickers(q: str = ""):
    """Mock endpoint for ticker autocomplete"""
    # In a real app, query a database or external API
    samples = ["AAPL", "MSFT", "NVDA", "TSLA", "SPY", "GOOGL", "AMZN", "META"]
    if q:
        q = q.upper()
        results = [t for t in samples if q in t]
    else:
        results = samples[:5]
    return {"results": results}

@app.get("/api/health")
def health_check():
    """Lightweight health check for frontend connectivity detection."""
    return {"status": "ok"}
