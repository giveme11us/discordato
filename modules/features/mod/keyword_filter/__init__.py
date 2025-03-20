"""
Discord bot module for filtering messages using keyword patterns.

This module provides functionality to automatically filter messages
containing specified patterns, such as scam links, invite links,
or other configurable keywords.
"""

__all__ = ["setup_keyword_filter"]

from .keyword_filter import setup_keyword_filter

import discord
from discord import app_commands
import logging
from .filter import process_message
from .config_cmd import keyword_filter_config, keyword_filter_quicksetup

logger = logging.getLogger('discord_bot.modules.mod.keyword_filter')

async def setup(bot):
    """
    Set up the keyword filter module.
    
    Args:
        bot: The bot instance
    """
    logger.info("Setting up Keyword Filter module")
    
    # Register the message handler
    bot.add_listener(on_message, "on_message")
    
    # Register the configuration command
    bot.tree.add_command(keyword_filter_config)
    bot.tree.add_command(keyword_filter_quicksetup)
    
    logger.info("Keyword Filter module setup complete")

async def on_message(message):
    """
    Process messages to check for filtered keywords.
    
    Args:
        message: The Discord message to check
    """
    # Skip bot messages but allow webhook messages
    if message.author.bot and not message.webhook_id:
        return
        
    await process_message(message) 