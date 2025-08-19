"""
Simple logging configuration for cAIber
"""

import logging
import sys
from datetime import datetime

def setup_logger(name="cAIber", level=logging.INFO):
    """Set up a simple logger with console and file output"""
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers = []
    
    # Console handler - only important messages
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console_format = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(console_format)
    
    # File handler - everything including debug
    log_file = f"caiber_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    
    logger.addHandler(console)
    logger.addHandler(file_handler)
    
    return logger

# Global logger instance
logger = setup_logger()