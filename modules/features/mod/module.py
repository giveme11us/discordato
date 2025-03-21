"""
Mod Module (DEPRECATED)

This module provides moderation and general utility commands.

WARNING: This module is deprecated and will be removed in a future version.
The bot now uses a cog-based architecture. Please use the cogs in the cogs/ directory instead.
"""

import logging
import discord
from discord import app_commands
from discord.ext import commands
from modules.features.mod.reaction_forward.reaction_forward import setup_reaction_forward
from modules.features.mod.link_reaction.link_reaction import setup_link_reaction

logger = logging.getLogger('discord_bot.modules.mod')
logger.warning("modules/mod/module.py is deprecated and will be removed in a future version. Use cogs instead.")

# Module information
NAME = "mod"
DESCRIPTION = "Moderation and general utility commands"

async def setup(bot):
    """
    Set up all mod features.
    
    Args:
        bot: The Discord bot instance
    """
    logger.info("Setting up mod features")
    
    # Set up reaction forward feature
    try:
        setup_reaction_forward(bot)
        logger.info("Set up reaction_forward feature")
    except Exception as e:
        logger.error(f"Failed to set up reaction_forward feature: {e}")
    
    # Set up link reaction feature
    try:
        setup_link_reaction(bot)
        logger.info("Set up link_reaction feature")
    except Exception as e:
        logger.error(f"Failed to set up link_reaction feature: {e}")
    
    logger.info("Finished setting up mod features")

def teardown(bot):
    """
    Clean up the mod module.
    
    Args:
        bot: The Discord bot to clean up
    """
    return True 