"""
Monitoring Module

This module provides system monitoring, health checks, metrics collection,
and maintenance utilities for the Discord bot.
"""

import logging
from typing import Optional, Set
import discord
from .module import setup as setup_monitoring
from .module import teardown as teardown_monitoring
from .commands import register_commands
from .maintenance_commands import register_maintenance_commands

logger = logging.getLogger(__name__)

async def setup(bot: discord.Client, registered_commands: Optional[Set[str]] = None) -> Set[str]:
    """
    Set up the monitoring module.
    
    Args:
        bot: The Discord bot instance
        registered_commands: Set of registered command names
        
    Returns:
        Set[str]: Updated set of registered command names
    """
    if registered_commands is None:
        registered_commands = set()
    
    try:
        # Set up monitoring system
        setup_monitoring(bot)
        
        # Register monitoring commands
        register_commands(bot, registered_commands)
        
        # Register maintenance commands
        register_maintenance_commands(bot, registered_commands)
        
        logger.info("Monitoring module initialized successfully")
    except Exception as e:
        logger.error(f"Error setting up monitoring module: {e}")
    
    return registered_commands

async def teardown(bot: discord.Client) -> None:
    """
    Clean up the monitoring module.
    
    Args:
        bot: The Discord bot instance
    """
    try:
        teardown_monitoring(bot)
        logger.info("Monitoring module shut down successfully")
    except Exception as e:
        logger.error(f"Error shutting down monitoring module: {e}")