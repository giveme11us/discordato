"""
Environment Variables Loader

This module handles loading environment variables from .env file
and provides access to configuration settings.
"""

import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger('discord_bot.environment')

def load_environment(env_file='.env'):
    """
    Load environment variables from specified file.
    
    Args:
        env_file (str): Path to the environment file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load environment variables from .env file
        if os.path.exists(env_file):
            load_dotenv(env_file)
            logger.info(f"Loaded environment from {env_file}")
            return True
        else:
            logger.warning(f"Environment file {env_file} not found")
            return False
    except Exception as e:
        logger.error(f"Error loading environment: {str(e)}")
        return False

def get_token(module_name=None):
    """
    Get the Discord token for a specific module.
    
    Args:
        module_name (str, optional): Name of the module. Defaults to None.
        
    Returns:
        str: The Discord token for the module or the main token if no module is specified.
    """
    if module_name:
        # Try to get module-specific token
        token_var = f"{module_name.upper()}_BOT_TOKEN"
        token = os.getenv(token_var)
        
        # If module-specific token not found, fall back to main token
        if not token:
            logger.warning(f"No token found for module {module_name}, falling back to main token")
            token = os.getenv('DISCORD_BOT_TOKEN')
        return token
    else:
        # Return main token
        return os.getenv('DISCORD_BOT_TOKEN')

def is_development():
    """
    Check if the application is running in development mode.
    
    Returns:
        bool: True if in development mode, False otherwise
    """
    return os.getenv('DEVELOPMENT', 'False').lower() in ('true', '1', 't') 