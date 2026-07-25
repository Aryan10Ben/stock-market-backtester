# Architecture

See the system design in the project README for the full module breakdown, data flow, and MVP scope.

## Layers

1. **Config** — Pydantic-validated settings from YAML, env vars, and CLI
2. **Data** — Fetch, validate, clean, and cache OHLCV bars
3. **Strategy** — Signal generation without look-ahead bias
4. **Engine** — Bar-by-bar simulation with next-bar execution
5. **Metrics** — Performance statistics and benchmark comparison
6. **Visualization** — Presentation-ready charts and reports

## Key Invariant

Signals at bar `t` use only data through bar `t`. Execution occurs at bar `t+1` open (or close, configurable).

## Data Flow

```
CLI/YAML → Config → Data Fetch → Validate → Clean → Strategy → Backtester → Metrics → Charts → Report
```
