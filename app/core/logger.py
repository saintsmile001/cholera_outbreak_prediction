"""
Application-wide logging configuration.

Provides a pre-configured logger that outputs timestamped, leveled messages
to the console.  Import `logger` anywhere in the project:

    from app.core.logger import logger
    logger.info("Server started")
"""

import logging
import sys


def _build_logger(name: str = "cholera_api") -> logging.Logger:
    """Create and configure the application logger."""

    log = logging.getLogger(name)

    # Prevent duplicate handlers if this function is called more than once
    if log.handlers:
        return log

    log.setLevel(logging.DEBUG)

    # ── Console handler ──────────────────────────────────────────────────
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console.setFormatter(formatter)
    log.addHandler(console)

    # Don't propagate to the root logger (avoids duplicate output)
    log.propagate = False

    return log


# Shared logger instance
logger = _build_logger()
