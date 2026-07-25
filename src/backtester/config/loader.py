"""Load and merge configuration from YAML files, CLI overrides, and env vars."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from backtester.config.settings import Settings
from backtester.utils.exceptions import ConfigError


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge override dict into base dict."""
    merged = base.copy()
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML file and return its contents as a dict."""
    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")

    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict):
        raise ConfigError(f"Config file must contain a YAML mapping: {path}")

    return data


def _parse_date(value: str | date) -> date:
    """Parse an ISO date string or pass through a date object."""
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


from backtester.utils.paths import resolve_path


def load_settings(
    config_path: Path | str | None = None,
    cli_overrides: dict[str, Any] | None = None,
) -> Settings:
    """
    Load settings by merging default YAML (if provided), and CLI overrides.
    Environment variables (BACKTESTER_*) are applied automatically by pydantic-settings.
    """
    config_data = {}

    if config_path:
        path = resolve_path(config_path)
        try:
            config_data = _load_yaml(path)
        except ConfigError:
            raise
        except yaml.YAMLError as exc:
            raise ConfigError(f"Failed to parse config file {path}: {exc}") from exc

    if cli_overrides:
        config_data = _deep_merge(config_data, cli_overrides)

    # Convert date strings from YAML to date objects before pydantic validation
    if "start_date" in config_data:
        config_data["start_date"] = _parse_date(config_data["start_date"])
    if "end_date" in config_data:
        config_data["end_date"] = _parse_date(config_data["end_date"])

    try:
        return Settings(**config_data)
    except ValidationError as exc:
        raise ConfigError(f"Invalid configuration:\n{exc}") from exc
