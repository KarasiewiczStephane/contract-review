"""Structured logging setup for the contract review application."""

import logging
import sys


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Create and configure a logger instance.

    Args:
        name: Logger name, typically the module's __name__.
        level: Logging level (default INFO).

    Returns:
        Configured Logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)
    return logger
