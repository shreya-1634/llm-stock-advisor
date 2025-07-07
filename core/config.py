import logging
import os
from logging.handlers import RotatingFileHandler
from colorlog import ColoredFormatter

def setup_logging():
    """Centralized logging configuration"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    os.makedirs('logs', exist_ok=True)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=2*1024*1024,  # 2MB
        backupCount=3
    )
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # Color console handler
    color_formatter = ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(name)s%(reset)s - %(message)s",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(color_formatter)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler]
    )
    logging.info("Logging system initialized")

def get_logger(name):
    """Get configured logger instance"""
    return logging.getLogger(name)
