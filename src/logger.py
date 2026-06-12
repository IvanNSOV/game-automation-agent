"""Logging utilities for the autonomous agent."""

import sys
from pathlib import Path
from loguru import logger


def setup_logger(level="INFO", log_file=None, verbose=False):
    """
    Configure logging for the application.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (None = console only)
        verbose: Enable verbose output
    
    Returns:
        Configured logger instance
    """
    # Remove default handler
    logger.remove()
    
    # Console output
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    
    if verbose:
        logger.add(sys.stdout, format=log_format, level=level, colorize=True)
    else:
        simple_format = "<level>{level: <8}</level> | <level>{message}</level>"
        logger.add(sys.stdout, format=simple_format, level=level, colorize=True)
    
    # File output if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            str(log_path),
            format=log_format,
            level=level,
            rotation="100 MB",
            retention="7 days",
        )
    
    return logger
