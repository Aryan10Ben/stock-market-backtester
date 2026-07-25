# Interview Preparation

## Resume Bullet Points

1. **Built a production-quality stock backtesting system in Python** with layered architecture (data, strategy, engine, metrics, visualization), Pydantic config validation, and 30+ unit/integration tests achieving reproducible, look-ahead-bias-free simulation results.

2. **Designed a deterministic backtesting engine** that simulates MA crossover trades with commission/slippage modeling, next-bar execution, and performance analytics (Sharpe ratio, max drawdown, win rate) benchmarked against buy-and-hold.

3. **Implemented robust data pipeline** with yfinance integration, retry logic, OHLCV validation, parquet caching, structured logging, and graceful error handling for API failures and invalid inputs.

## 30-Second Explanation

"I built a Python backtesting system that downloads historical stock data, runs a moving-average crossover strategy through a simulated trading engine, and outputs performance metrics and charts. The architecture is layered — data, strategy, engine, metrics, and visualization — with strict separation to prevent look-ahead bias. Signals are generated on bar t and executed on bar t+1. It's config-driven, fully tested, and designed to be easy to extend with new strategies."

## 2-Minute Explanation

"I designed and built a stock market backtesting system as a portfolio project demonstrating software engineering best practices for quantitative finance.

The system follows a unidirectional pipeline: configuration is loaded and validated through Pydantic models from YAML files, environment variables, or CLI arguments. The data layer fetches OHLCV bars from yfinance with retry logic, validates schema and sanity checks, and optionally caches to parquet.

The strategy layer implements a moving average crossover — buy when the fast MA crosses above the slow MA, sell on the reverse. Critically, signals at bar t only use data through bar t, and the engine executes on the next bar's open price to avoid look-ahead bias.

The backtesting engine tracks cash, holdings, and portfolio value bar-by-bar, applying configurable commission and slippage. It records every trade and builds an equity curve alongside a buy-and-hold benchmark.

The metrics layer computes total return, CAGR, Sharpe ratio, max drawdown, and win rate. The visualization layer generates price charts with buy/sell markers, equity curves, and drawdown plots.

I wrote 30+ tests covering config validation, data integrity, strategy signals, portfolio math, and a full end-to-end integration test. The project is structured to be interview-friendly — each module has a single responsibility and the design supports adding new strategies without modifying the engine."

## Likely Interview Questions & Answers

### Q: How do you prevent look-ahead bias?

**A:** The strategy generates signals using only data available at bar t. The backtester executes those signals on bar t+1's open price. The strategy never accesses future bars, and this is enforced in the engine loop and tested explicitly.

### Q: Why layered architecture instead of a single script?

**A:** Separation of concerns makes each component independently testable and replaceable. I can swap the data source, add a new strategy, or change execution rules without touching unrelated code. This mirrors how production trading systems are structured.

### Q: How do you handle bad or missing data?

**A:** The validator rejects empty data, non-monotonic dates, non-positive prices, and insufficient bar counts. The cleaner drops null OHLC rows and forward-fills minor gaps. Suspicious data like zero-volume days or large price jumps trigger warnings in logs but don't silently corrupt results.

### Q: How is the system configured?

**A:** Three layers merge: a default YAML file, optional environment variables prefixed with BACKTESTER_, and CLI overrides. Pydantic validates everything at startup — invalid tickers, date ranges, or negative capital fail fast with clear messages.

### Q: What would you add next?

**A:** A strategy registry for plug-in strategies, multi-ticker portfolio support, walk-forward out-of-sample testing, and a parameter sweep tool. I'd also add SQLite caching and a Streamlit dashboard for interactive exploration.

### Q: How do you test a backtesting system?

**A:** Unit tests for each layer with synthetic deterministic data — known price patterns that produce predictable crossover signals. Portfolio tests verify cash/holding math. Integration tests run the full pipeline on fixture CSVs and verify output files are generated. I also test determinism: same inputs always produce identical results.

### Q: What's the execution model?

**A:** Full-position, long-only trades. On a BUY signal, the engine invests all available cash (integer shares, floor division). On SELL, it closes the entire position. Commission is a percentage of trade value; slippage is applied in basis points to the execution price.
