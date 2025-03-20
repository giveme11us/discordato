"""
In-store Module

This module contains features related to in-store product monitoring and management.
"""

import logging

logger = logging.getLogger('discord_bot.modules.instore')

def setup(bot, registered_commands=None):
    """
    Set up the in-store module for a bot.
    
    Args:
        bot: The Discord bot to set up
        registered_commands: Set of already registered commands to avoid duplicates
    
    Returns:
        Set of registered commands
    """
    if registered_commands is None:
        registered_commands = set()
    
    logger.info("Setting up in-store module")
    
    # Module is being prepared for future features
    logger.info("In-store module structure ready for future features")
    
    # Register the help command
    if 'instore_help' not in registered_commands:
        try:
            from modules.instore.help_cmd import setup_help_cmd
            setup_help_cmd(bot)
            logger.info("Registered instore_help command")
            registered_commands.add('instore_help')
        except Exception as e:
            logger.error(f"Could not register instore_help command: {str(e)}")
    
    return registered_commands

def teardown(bot):
    """
    Tear down the in-store module.
    
    Args:
        bot: The Discord bot to tear down
    """
    logger.info("Tearing down in-store module") 