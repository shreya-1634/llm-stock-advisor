import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging():
    """Centralized logging configuration with file rotation"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    log_date = datetime.now().strftime("%Y-%m-%d")
    log_dir = f"logs/{log_date}"
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            RotatingFileHandler(
                f'{log_dir}/app.log',
                maxBytes=2*1024*1024,
                backupCount=3,
                encoding='utf-8'
            )
        ]
    )
    
    tf_logger = logging.getLogger('tensorflow')
    tf_logger.setLevel(logging.WARNING)
    
    logging.info("Logging system initialized at %s", log_dir)

def get_logger(name):
    """Get pre-configured logger with module-specific formatting"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        try:
            from colorlog import ColoredFormatter
            color_formatter = ColoredFormatter(
                "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(name)s%(reset)s - %(message)s",
                datefmt=None,
                reset=True,
                log_colors={
                    'DEBUG':    'cyan',
                    'INFO':     'green',
                    'WARNING':  'yellow',
                    'ERROR':    'red',
                    'CRITICAL': 'red,bg_white',
                }
            )
            console = logging.StreamHandler()
            console.setFormatter(color_formatter)
            logger.addHandler(console)
        except ImportError:
            console = logging.StreamHandler()
            console.setFormatter(formatter)
            logger.addHandler(console)
    
    return logger
