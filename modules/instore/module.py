"""
Instore Module

This module provides commands for in-store interactions.
"""

import logging
import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger('discord_bot.modules.instore')

# Module information
NAME = "instore"
DESCRIPTION = "In-store interaction commands"

def setup(bot, registered_commands=None):
    """
    Set up the instore module.
    
    Args:
        bot: The Discord bot instance
        registered_commands (set, optional): Set of already registered command names
    """
    logger.info("Setting up instore module")
    
    # Initialize registered_commands if not provided
    if registered_commands is None:
        registered_commands = set()
    
    # Register commands if not already registered
    if 'number' not in registered_commands:
        try:
            from modules.instore.number import setup_number
            setup_number(bot)
            logger.info("Registered number command")
        except Exception as e:
            logger.warning(f"Could not register number command: {str(e)}")
    else:
        logger.info("Number command already registered, skipping")
    
    # Register event handlers
    @bot.event
    async def on_guild_join(guild):
        # Log guild join
        logger.info(f"Bot joined guild: {guild.name} (ID: {guild.id})")
        
        # Find a suitable channel to send welcome message
        system_channel = guild.system_channel
        if system_channel and system_channel.permissions_for(guild.me).send_messages:
            await system_channel.send("Thanks for adding me to your server! Use `/help` to see available commands.")

def teardown(bot):
    """
    Clean up the instore module.
    
    Args:
        bot: The Discord bot instance
    """
    logger.info("Tearing down instore module") 