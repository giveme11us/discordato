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

logger = logging.getLogger('discord_bot.modules.mod')
logger.warning("modules/mod/module.py is deprecated and will be removed in a future version. Use cogs instead.")

# Module information
NAME = "mod"
DESCRIPTION = "Moderation and general utility commands"

def setup(bot, registered_commands=None):
    """
    Set up the mod module.
    
    Args:
        bot: The Discord bot to set up
        registered_commands: A set of already registered commands
    """
    logger.warning("modules/mod/__init__.py is deprecated and will be removed in a future version. Use cogs instead.")
    
    if registered_commands is None:
        registered_commands = set()
    
    # Import and set up the link reaction feature
    from modules.mod.link_reaction.link_reaction import setup_link_reaction
    setup_link_reaction(bot)
    
    # Import and set up the remover feature with user command
    from modules.mod.link_reaction.remover import setup_remover_commands
    setup_remover_commands(bot)
    
    # Import and set up the keyword filter feature
    from modules.mod.keyword_filter.keyword_filter import setup_keyword_filter
    setup_keyword_filter(bot)
    
    # Import and set up the reaction forward feature
    from modules.mod.reaction_forward.reaction_forward import setup_reaction_forward
    setup_reaction_forward(bot)
    
    # Import and set up the pinger feature
    from modules.mod.pinger.pinger import setup_pinger
    setup_pinger(bot)
    
    return True

def teardown(bot):
    """
    Clean up the mod module.
    
    Args:
        bot: The Discord bot to clean up
    """
    return True 