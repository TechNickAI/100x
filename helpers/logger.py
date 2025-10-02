"""Logging configuration using Loguru."""

import sys

from loguru import logger

from ai.core.config import config

# Global logging configuration for loguru
logger.remove()
logger_format = (
    # Put message first so tags for structured logging come first
    "<level>{time}</level> {message} | <level>{level}</level> "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>"
)
logger.add(sys.stderr, catch=True, format=logger_format, level=config.log_level)
logger = logger.opt(colors=True)

__all__ = ["logger"]
