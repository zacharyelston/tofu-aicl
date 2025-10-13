"""Logging configuration - small, focused file"""

import sys
from loguru import logger


def setup_logging(verbose: bool = False) -> logger:
    """
    Configure structured logging with Loguru
    
    Single responsibility: logging setup
    """
    logger.remove()  # Remove default handler
    
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan> | "
        "<level>{message}</level>"
    )
    
    level = "DEBUG" if verbose else "INFO"
    
    # Console handler
    logger.add(
        sys.stderr,
        format=log_format,
        level=level,
        colorize=True,
    )
    
    # File handler
    logger.add(
        "logs/aicl_{time}.log",
        rotation="10 MB",
        retention="1 week",
        level="DEBUG",
        format=log_format,
    )
    
    return logger
