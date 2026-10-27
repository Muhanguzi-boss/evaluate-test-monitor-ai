import os
from pathlib import Path

# Must run before logging_config is imported by the tests.
os.environ.setdefault("APP_LOG_FILE", str(Path(__file__).resolve().parent / "logs" / "test.log"))


def pytest_configure(config):
    config.addinivalue_line("markers", "live: calls the real Anthropic API (needs ANTHROPIC_API_KEY)")
