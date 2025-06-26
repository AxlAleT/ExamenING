import logging
import os
from logging.handlers import RotatingFileHandler
from config.settings import LOGGING_LEVEL, LOGGING_FORMAT, LOG_FILE_PATH

def setup_logging(name, log_file=None):
    """
    Set up logging configuration.
    
    Args:
        name (str): Logger name, typically __name__ of the calling module
        log_file (str, optional): Path to the log file. If None, uses the default from settings.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    if log_file is None:
        log_file = LOG_FILE_PATH
        
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOGGING_LEVEL))
    
    # Add a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, LOGGING_LEVEL))
    console_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
    logger.addHandler(console_handler)
    
    # Add file handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, LOGGING_LEVEL))
    file_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
    logger.addHandler(file_handler)
    
    return logger

# Create a default logger
logger = setup_logging('etl_system')