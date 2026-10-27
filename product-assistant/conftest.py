import os
from pathlib import Path

os.environ.setdefault("APP_LOG_FILE", str(Path(__file__).resolve().parent / "logs" / "test.log"))


def pytest_configure(config):
    config.addinivalue_line("markers", "live: calls the real Anthropic API (needs ANTHROPIC_API_KEY)")
