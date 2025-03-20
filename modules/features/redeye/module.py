"""
Redeye Module

Module for handling Redeye functionality.
"""

import logging

logger = logging.getLogger('discord_bot.modules.redeye')

def setup(bot, registered_commands=None):
    """
    Set up the redeye module.
    
    Args:
        bot: The Discord bot to set up
        registered_commands: A set of already registered commands
    """
    logger.info("Setting up redeye module")
    
    if registered_commands is None:
        registered_commands = set()
    
    # Register the profile viewer command
    if 'redeye-profiles' not in registered_commands:
        try:
            from modules.features.redeye.profile_cmd import setup_profile_cmd
            setup_profile_cmd(bot)
            logger.info("Registered redeye-profiles command")
            registered_commands.add('redeye-profiles')
        except Exception as e:
            logger.error(f"Could not register redeye-profiles command: {str(e)}")
    
    # Register the help command
    if 'redeye_help' not in registered_commands:
        try:
            from modules.features.redeye.help_cmd import setup_help_cmd
            setup_help_cmd(bot)
            logger.info("Registered redeye_help command")
            registered_commands.add('redeye_help')
        except Exception as e:
            logger.error(f"Could not register redeye_help command: {str(e)}")
    
    return True

def teardown(bot):
    """
    Clean up the redeye module.
    
    Args:
        bot: The Discord bot to clean up
    """
    logger.info("Tearing down redeye module")
    return True 