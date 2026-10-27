"""Central logging setup: writes to logs/app.log (and the console)."""

import logging
import os
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent / "logs"
# Tests set APP_LOG_FILE so they don't pollute the real app.log metrics.
LOG_FILE = Path(os.getenv("APP_LOG_FILE", LOG_DIR / "app.log"))
LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure the 'product_assistant' logger once and return it."""
    logger = logging.getLogger("product_assistant")
    if logger.handlers:  # already configured (e.g. imported twice)
        return logger

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter(LOG_FORMAT)

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)  # keep the console quiet

    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False
    return logger


def get_logger(name: str) -> logging.Logger:
    """Child logger, e.g. get_logger('tools') -> 'product_assistant.tools'."""
    setup_logging()
    return logging.getLogger(f"product_assistant.{name}")
