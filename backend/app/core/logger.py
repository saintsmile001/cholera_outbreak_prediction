"""
Application-wide logging configuration.

Provides a pre-configured logger that outputs timestamped, leveled messages
to the console.  Import `logger` anywhere in the project:

    from app.core.logger import logger
    logger.info("Server started")
"""

import logging
import sys


_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FMT = "%Y-%m-%d %H:%M:%S"


def _configure_root_logger() -> None:
    """
    Configure the root logger once so all child loggers (email_service,
    send_email, etc.) inherit INFO-level output to stdout.
    Railway streams stdout directly to its log viewer.
    """
    root = logging.getLogger()
    if root.handlers:
        # Already configured — just ensure the level is right
        root.setLevel(logging.INFO)
        return

    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(fmt=_FORMAT, datefmt=_DATE_FMT))
    root.addHandler(handler)


def _build_logger(name: str = "cholera_api") -> logging.Logger:
    """Create and configure the application logger."""
    _configure_root_logger()
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    return log


# Shared logger instance
logger = _build_logger()
