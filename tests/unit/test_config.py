"""Tests for configuration loading and validation."""

from datetime import date
from pathlib import Path

import pytest

from backtester.config.loader import load_settings
from backtester.utils.exceptions import ConfigError


def test_load_default_config(default_config_path: Path) -> None:
    settings = load_settings(config_path=default_config_path)
    assert settings.ticker == "AAPL"
    assert settings.start_date == date(2020, 1, 1)
    assert settings.end_date == date(2024, 12, 31)
    assert settings.initial_cash == 100_000.0
    assert settings.strategy.fast_window == 20
    assert settings.strategy.slow_window == 50


def test_cli_overrides(default_config_path: Path) -> None:
    settings = load_settings(
        config_path=default_config_path,
        cli_overrides={"ticker": "MSFT", "initial_cash": 50_000.0},
    )
    assert settings.ticker == "MSFT"
    assert settings.initial_cash == 50_000.0


def test_invalid_ticker_rejected(default_config_path: Path) -> None:
    with pytest.raises(ConfigError, match="Invalid ticker"):
        load_settings(
            config_path=default_config_path,
            cli_overrides={"ticker": "INVALID TICKER!"},
        )


def test_invalid_date_range_rejected(default_config_path: Path) -> None:
    with pytest.raises(ConfigError, match="start_date"):
        load_settings(
            config_path=default_config_path,
            cli_overrides={
                "start_date": date(2024, 1, 1),
                "end_date": date(2020, 1, 1),
            },
        )


def test_fast_window_must_be_less_than_slow(default_config_path: Path) -> None:
    with pytest.raises(ConfigError, match="fast_window"):
        load_settings(
            config_path=default_config_path,
            cli_overrides={"strategy": {"fast_window": 50, "slow_window": 20}},
        )
