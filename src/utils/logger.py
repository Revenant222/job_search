"""
Logging utilities for AI Job Filter Agent.
"""
import logging
import os
from datetime import datetime
from typing import Optional
from config.settings import LOG_LEVEL


def setup_logger(name: str, log_file: Optional[str] = None, level: str = LOG_LEVEL) -> logging.Logger:
    """
    Set up a logger with console and optional file output.
    
    Args:
        name: Logger name
        log_file: Optional log file path
        level: Logging level
        
    Returns:
        Configured logger
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if log_file is specified
    if log_file:
        # Ensure logs directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_app_logger() -> logging.Logger:
    """
    Get the main application logger.
    
    Returns:
        Application logger
    """
    log_file = f"logs/app_{datetime.now().strftime('%Y%m%d')}.log"
    return setup_logger("job_filter_agent", log_file)


def get_error_logger() -> logging.Logger:
    """
    Get the error logger.
    
    Returns:
        Error logger
    """
    log_file = f"logs/error_{datetime.now().strftime('%Y%m%d')}.log"
    return setup_logger("job_filter_agent.error", log_file)


def get_verification_logger() -> logging.Logger:
    """
    Get the verification logger.
    
    Returns:
        Verification logger
    """
    log_file = f"logs/verification_{datetime.now().strftime('%Y%m%d')}.log"
    return setup_logger("job_filter_agent.verification", log_file)


# Create default loggers
app_logger = get_app_logger()
error_logger = get_error_logger()
verification_logger = get_verification_logger() 