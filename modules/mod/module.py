"""
Mod Module

This module provides moderation and general utility commands.
"""

import logging
import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger('discord_bot.modules.mod')

# Module information
NAME = "mod"
DESCRIPTION = "Moderation and general utility commands"

def setup(bot, registered_commands=None):
    """
    Set up the mod module.
    
    Args:
        bot: The Discord bot instance
        registered_commands (set, optional): Set of already registered command names
    """
    logger.info("Setting up mod module")
    
    # Initialize registered_commands if not provided
    if registered_commands is None:
        registered_commands = set()
    
    # Register commands if not already registered
    if 'ping' not in registered_commands:
        try:
            from modules.mod.general.ping import setup_ping
            setup_ping(bot)
            logger.info("Registered ping command")
        except Exception as e:
            logger.warning(f"Could not register ping command: {str(e)}")
    else:
        logger.info("Ping command already registered, skipping")
    
    # Register event handlers
    @bot.event
    async def on_message(message):
        # Ignore messages from bots
        if message.author.bot:
            return
        
        # Process commands
        await bot.process_commands(message)
        
        # Log message
        logger.debug(f"Message from {message.author}: {message.content}")

def teardown(bot):
    """
    Clean up the mod module.
    
    Args:
        bot: The Discord bot instance
    """
    logger.info("Tearing down mod module") 