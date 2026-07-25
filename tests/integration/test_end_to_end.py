"""End-to-end integration test for the backtesting pipeline."""

from pathlib import Path

import pytest

from backtester.cli import main


def test_full_pipeline_run_with_csv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Run the full backtest via CLI using a local CSV to avoid network calls."""
    # Setup paths
    fixture_csv = Path("tests/fixtures/AAPL_sample.csv")
    if not fixture_csv.exists():
        pytest.skip("Fixture data not found")

    output_dir = tmp_path / "outputs"

    # Run CLI
    args = [
        "--ticker", "AAPL",
        "--start", "2023-01-01",
        "--end", "2023-03-31",
        "--csv", str(fixture_csv)
    ]

    # We don't monkeypatch env vars since the YAML default takes precedence.
    # We'll just check the real outputs directory.
    output_dir = Path("outputs")

    exit_code = main(args)
    assert exit_code == 0

    # Verify outputs were created (find the newest one)
    run_dirs = sorted(output_dir.glob("AAPL_*"))
    assert len(run_dirs) >= 1

    run_dir = run_dirs[-1]
    assert (run_dir / "price_signals.png").exists()
    assert (run_dir / "equity_curve.png").exists()
    assert (run_dir / "drawdown.png").exists()
