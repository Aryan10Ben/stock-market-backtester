"""Pydantic settings models for backtest configuration."""

from __future__ import annotations

import re
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

TICKER_PATTERN = re.compile(r"^[A-Z0-9.]{1,10}$")


class StrategySettings(BaseModel):
    """Strategy parameters."""

    name: Literal["ma_crossover", "rsi", "macd", "bollinger", "buy_hold"] = "ma_crossover"

    # MA Crossover
    fast_window: int = Field(default=20, ge=2, le=500)
    slow_window: int = Field(default=50, ge=3, le=500)

    # RSI
    rsi_period: int = Field(default=14, ge=2, le=100)
    rsi_overbought: float = Field(default=70.0, ge=50.0, le=100.0)
    rsi_oversold: float = Field(default=30.0, ge=0.0, le=50.0)

    # MACD
    macd_fast: int = Field(default=12, ge=2, le=100)
    macd_slow: int = Field(default=26, ge=2, le=200)
    macd_signal: int = Field(default=9, ge=2, le=100)

    # Bollinger Bands
    bb_period: int = Field(default=20, ge=2, le=200)
    bb_std: float = Field(default=2.0, ge=0.1, le=5.0)

    signal_on: Literal["open", "high", "low", "close"] = "close"

    @model_validator(mode="after")
    def validate_strategy_params(self) -> StrategySettings:
        if self.name == "ma_crossover":
            if self.fast_window >= self.slow_window:
                raise ValueError(
                    f"fast_window ({self.fast_window}) must be less than "
                    f"slow_window ({self.slow_window})"
                )
        elif self.name == "macd":
            if self.macd_fast >= self.macd_slow:
                raise ValueError("macd_fast must be less than macd_slow")
        return self


class ExecutionSettings(BaseModel):
    """Order execution simulation parameters."""

    price: Literal["open", "close"] = "open"
    position_sizing: Literal["full"] = "full"


class DataSettings(BaseModel):
    """Data fetching and caching parameters."""

    cache_enabled: bool = True
    cache_dir: str = "data/cache"
    min_bars_buffer: int = Field(default=10, ge=0, le=100)


class OutputSettings(BaseModel):
    """Output directory and chart rendering parameters."""

    dir: str = "outputs"
    chart_dpi: int = Field(default=300, ge=72, le=600)


class LoggingSettings(BaseModel):
    """Logging configuration."""

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_dir: str = "logs"
    log_file: str = "backtester.log"


class MetricsSettings(BaseModel):
    """Performance metrics calculation parameters."""

    risk_free_rate: float = Field(
        default=0.05,
        ge=0.0,
        le=0.25,
        description="Annual risk-free rate for Sharpe ratio (e.g. 0.05 = 5%)",
    )
    trading_days_per_year: int = Field(default=252, ge=200, le=365)


class Settings(BaseSettings):
    """Top-level backtest configuration."""

    model_config = SettingsConfigDict(
        env_prefix="BACKTESTER_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    ticker: str = "AAPL"
    start_date: date = Field(default_factory=lambda: date.today() - __import__('datetime').timedelta(days=365))
    end_date: date = Field(default_factory=date.today)
    initial_cash: float = Field(default=100_000.0, gt=0)
    commission_rate: float = Field(default=0.001, ge=0, le=0.1)
    slippage_bps: float = Field(default=5.0, ge=0, le=100)

    strategy: StrategySettings = Field(default_factory=StrategySettings)
    execution: ExecutionSettings = Field(default_factory=ExecutionSettings)
    data: DataSettings = Field(default_factory=DataSettings)
    output: OutputSettings = Field(default_factory=OutputSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    metrics: MetricsSettings = Field(default_factory=MetricsSettings)

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not TICKER_PATTERN.match(normalized):
            raise ValueError(
                f"Invalid ticker '{value}'. Use 1-10 alphanumeric characters or dots (e.g. AAPL, BRK.B)."
            )
        return normalized

    @model_validator(mode="after")
    def validate_date_range(self) -> Settings:
        if self.start_date >= self.end_date:
            raise ValueError(
                f"start_date ({self.start_date}) must be before end_date ({self.end_date})"
            )
        if self.end_date > date.today():
            raise ValueError(f"end_date ({self.end_date}) cannot be in the future")
        return self

    @property
    def min_required_bars(self) -> int:
        """Minimum number of bars needed for a valid backtest."""
        base_buffer = self.data.min_bars_buffer
        if self.strategy.name == "ma_crossover":
            return self.strategy.slow_window + base_buffer
        elif self.strategy.name == "rsi":
            return self.strategy.rsi_period + base_buffer
        elif self.strategy.name == "macd":
            return self.strategy.macd_slow + base_buffer
        elif self.strategy.name == "bollinger":
            return self.strategy.bb_period + base_buffer
        return base_buffer
