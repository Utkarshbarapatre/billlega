import logging
import sys
from typing import Dict, Any

def setup_logging(level: str = "INFO") -> None:
    """Setup application logging"""
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    root_logger.addHandler(console_handler)
    
    # Setup specific loggers
    loggers = [
        'backend',
        'uvicorn',
        'fastapi',
        'sqlalchemy.engine'
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, level.upper()))

def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name)
