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
        bot: The Discord bot to add commands to
        registered_commands: Set of already registered commands
    """
    logger.warning("modules/mod/__init__.py is deprecated and will be removed in a future version. Use cogs instead.")
    
    if registered_commands is None:
        registered_commands = set()
    
    # Import and set up the link reaction feature
    from modules.features.mod.link_reaction.link_reaction import setup_link_reaction
    setup_link_reaction(bot)
    
    # Import and set up the remover feature with user command
    from modules.features.mod.link_reaction.remover import setup_remover_commands
    setup_remover_commands(bot)
    
    # Import and set up the keyword filter feature
    from modules.features.mod.keyword_filter.keyword_filter import setup_keyword_filter
    setup_keyword_filter(bot)
    
    # Import and set up the reaction forward feature
    from modules.features.mod.reaction_forward.reaction_forward import setup_reaction_forward
    setup_reaction_forward(bot)
    
    # Import and set up the pinger feature
    from modules.features.mod.pinger.pinger import setup_pinger
    setup_pinger(bot)
    
    # Register mod_help command
    if 'mod_help' not in registered_commands:
        try:
            from modules.features.mod.help_cmd import setup_help_cmd
            setup_help_cmd(bot)
            registered_commands.add('mod_help')
            logger.info("Registered mod_help command")
        except Exception as e:
            logger.error(f"Could not register mod_help command: {str(e)}")
    
    return registered_commands

def teardown(bot):
    """
    Clean up the mod module.
    
    Args:
        bot: The Discord bot to clean up
    """
    return True 