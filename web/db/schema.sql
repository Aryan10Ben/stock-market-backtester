CREATE TABLE IF NOT EXISTS price_cache (
  ticker TEXT NOT NULL,
  date DATE NOT NULL,
  open NUMERIC, high NUMERIC, low NUMERIC, close NUMERIC, volume BIGINT,
  source TEXT NOT NULL,        -- 'yfinance' | 'stooq' | 'sample'
  fetched_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (ticker, date)
);

CREATE TABLE IF NOT EXISTS backtest_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  ticker TEXT NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  params JSONB NOT NULL,       -- strategy + capital/commission/slippage config
  metrics JSONB NOT NULL       -- CAGR, Sharpe, max drawdown, win rate, etc.
);
