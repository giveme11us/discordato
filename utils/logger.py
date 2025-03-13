"""
Logger Utility

This module provides logging functionality for the Discord bot.
"""

import logging
import os
from datetime import datetime

def setup_logger(name, log_level=logging.INFO, log_to_file=False, log_dir='logs'):
    """
    Set up a logger with the specified name and configuration.
    
    Args:
        name (str): The name of the logger
        log_level (int, optional): The logging level. Defaults to logging.INFO.
        log_to_file (bool, optional): Whether to log to a file. Defaults to False.
        log_dir (str, optional): The directory to store log files. Defaults to 'logs'.
    
    Returns:
        logging.Logger: The configured logger
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if requested
    if log_to_file:
        # Create log directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Create log file name with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(log_dir, f"{name.replace('.', '_')}_{timestamp}.log")
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_module_logger(module_name):
    """
    Get a logger for a specific module.
    
    Args:
        module_name (str): The name of the module
    
    Returns:
        logging.Logger: The module logger
    """
    return logging.getLogger(f"discord_bot.modules.{module_name}") 