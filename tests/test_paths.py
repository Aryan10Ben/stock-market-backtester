import os
import tempfile

from backtester.config.loader import load_settings
from backtester.config.settings import Settings


def test_load_settings_from_different_cwd():
    """
    Ensure that loading settings does not depend on the current working directory.
    This simulates the Vercel Serverless environment where the CWD is NOT the repository root.
    """
    original_cwd = os.getcwd()

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        try:
            # This should succeed without raising ConfigError for missing config/default.yaml
            settings = load_settings()

            assert isinstance(settings, Settings)
            assert settings.ticker == "AAPL" # Default ticker
        finally:
            os.chdir(original_cwd)
