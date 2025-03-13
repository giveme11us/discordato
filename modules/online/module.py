"""
Online Module

This module provides commands for online interactions.
"""

import logging
import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger('discord_bot.modules.online')

# Module information
NAME = "online"
DESCRIPTION = "Online interaction commands"

def setup(bot, registered_commands=None):
    """
    Set up the online module.
    
    Args:
        bot: The Discord bot instance
        registered_commands (set, optional): Set of already registered command names
    """
    logger.info("Setting up online module")
    
    # Initialize registered_commands if not provided
    if registered_commands is None:
        registered_commands = set()
    
    # Register commands if not already registered
    if 'hi' not in registered_commands:
        try:
            from modules.online.hi import setup_hi
            setup_hi(bot)
            logger.info("Registered hi command")
        except Exception as e:
            logger.warning(f"Could not register hi command: {str(e)}")
    else:
        logger.info("Hi command already registered, skipping")
    
    # Register event handlers
    @bot.event
    async def on_member_join(member):
        # Log member join
        logger.info(f"Member joined: {member}")
        
        # Send welcome message
        try:
            await member.send(f"Welcome to the server, {member.mention}!")
        except discord.errors.Forbidden:
            logger.warning(f"Could not send welcome message to {member}")

def teardown(bot):
    """
    Clean up the online module.
    
    Args:
        bot: The Discord bot instance
    """
    logger.info("Tearing down online module") 