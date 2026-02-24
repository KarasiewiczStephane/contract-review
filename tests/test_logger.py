"""Tests for logger setup."""

import logging

from src.utils.logger import setup_logger


def test_setup_logger() -> None:
    """Test logger creation and configuration."""
    logger = setup_logger("test_logger")
    assert logger.name == "test_logger"
    assert logger.level == logging.INFO
    assert len(logger.handlers) >= 1


def test_setup_logger_custom_level() -> None:
    """Test logger with custom log level."""
    logger = setup_logger("test_debug", level=logging.DEBUG)
    assert logger.level == logging.DEBUG


def test_setup_logger_no_duplicate_handlers() -> None:
    """Test that calling setup_logger twice doesn't duplicate handlers."""
    logger = setup_logger("test_no_dup")
    handler_count = len(logger.handlers)
    setup_logger("test_no_dup")
    assert len(logger.handlers) == handler_count
