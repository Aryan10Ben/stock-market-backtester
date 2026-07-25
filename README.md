# Stock Market Backtesting System

**Live Demo (Vercel):** [https://stock-market-backtester.vercel.app](https://stock-market-backtester.vercel.app) *(Note: History saving requires `DATABASE_URL` to be configured in Vercel settings)*

A production-quality Python backtesting framework for evaluating trading strategies on historical stock data. Built with clean layered architecture, input validation, deterministic simulation, and presentation-ready output.

## Features

- **Historical data fetching** via yfinance with retry logic and optional parquet cache
- **Data validation and cleaning** with schema checks and suspicious-data warnings
- **Moving average crossover strategy** (configurable windows, no look-ahead bias)
- `backtester.engine`: Core event loop and trade simulation.

## Deployment Topology (Next.js + Vercel)
If you deploy this repository as a Next.js full-stack app on Vercel, the Root Directory in Vercel settings MUST be set to `web/`.
Since Vercel serverless builds only bundle files contained within the configured Root Directory, any top-level directories (`config/`, `data/`, `src/`) are unreachable directly via disk I/O in production.
The Python API (`web/api/index.py`) overcomes this by:
1. Hardcoding `../src` in `requirements.txt` to install the `src` module directly into the serverless function's isolated environment.
2. Avoiding explicit `open("config/default.yaml")` disk reads. Configuration defaults are strictly maintained as typed Pydantic models.
3. Using `resolve_path()` internally to correctly infer paths from the installation directory rather than relying on `os.getcwd()`.

- **Backtesting engine** with next-bar execution, commission, and slippage modeling
- **Performance metrics**: total return, CAGR, Sharpe ratio, max drawdown, win rate, buy-and-hold benchmark
- **Charts**: price + signals, equity curve, drawdown
- **Config-driven**: YAML + environment variables + CLI overrides
- **Structured logging** to console and file
- **30+ unit and integration tests**

## Architecture

```
CLI/YAML Config
      │
      ▼
  Data Layer ──► Fetch → Validate → Clean
      │
      ▼
  Strategy Layer ──► MA Crossover signals (no look-ahead)
      │
      ▼
  Engine Layer ──► Portfolio + Executor (next-bar execution)
      │
      ▼
  Metrics Layer ──► Sharpe, drawdown, win rate, etc.
      │
      ▼
  Visualization ──► Charts + report.txt
```

See [docs/architecture.md](docs/architecture.md) for the full design.

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
cd "Stock Market Backtester"
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Run a Backtest

```bash
# Using default config (AAPL, 2020–2024)
python -m backtester

# Custom ticker and date range
python -m backtester --ticker MSFT --start 2019-01-01 --end 2023-12-31

# Using a custom config file
python -m backtester --config config/default.yaml

# Using fixture CSV (no network required)
python -m backtester --csv tests/fixtures/AAPL_sample.csv --ticker AAPL --start 2020-01-01 --end 2020-06-30
```

### Run Tests

```bash
pytest
```

## Next.js Web Dashboard

The project includes a production-ready Next.js web dashboard that connects to a serverless FastAPI backend (Vercel edge).

### Start the Local Web App
Make sure your Neon Database URL is configured:
```bash
export DATABASE_URL="postgresql://user:password@endpoint/dbname"
```

Start the Vercel dev server (runs both Next.js and FastAPI):
```bash
npx vercel dev
```
Navigate to [http://localhost:3000](http://localhost:3000) to view the dashboard.

## Configuration

Default settings live in [config/default.yaml](config/default.yaml):

```yaml
ticker: AAPL
start_date: "2020-01-01"
end_date: "2024-12-31"
initial_cash: 100000.0
commission_rate: 0.001
slippage_bps: 5
execution_price: open

strategy:
  name: ma_crossover
  fast_window: 20
  slow_window: 50
```

Override via environment variables (prefix `BACKTESTER_`):

```bash
export BACKTESTER_TICKER=GOOGL
export BACKTESTER_INITIAL_CASH=50000
python -m backtester
```

## Output

Each run creates a timestamped folder under `outputs/`:

```
outputs/AAPL_20260724_143000/
├── price_signals.png
├── equity_curve.png
├── drawdown.png
└── report.txt
```

## Project Structure

```
src/backtester/
├── cli.py              # CLI entry point
├── pipeline.py         # Orchestration
├── config/             # Settings and loader
├── data/               # Fetch, validate, clean, cache
├── strategy/           # MA crossover strategy
├── engine/             # Backtester, portfolio, executor
├── metrics/            # Performance calculations
├── visualization/      # Chart generation
├── models/             # Domain types
└── utils/                # Logging, exceptions
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Next-bar execution | Prevents look-ahead bias |
| Pydantic config | Fail-fast validation at startup |
| Layered architecture | Testable, extensible, interview-friendly |
| Integer share sizing | Realistic for retail execution |
| Buy-and-hold benchmark | Context for strategy performance |

## Interview Prep

See [docs/interview_prep.md](docs/interview_prep.md) for resume bullets, elevator pitches, and Q&A.

## License

MIT
