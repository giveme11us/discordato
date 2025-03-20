"""
Moderation Module (DEPRECATED)

This module provides various moderation features for Discord servers.

WARNING: This direct module approach is deprecated and will be removed in a future version.
The bot now uses a cog-based architecture. Please use the cogs in the cogs/ directory instead.
"""

import logging
logger = logging.getLogger('discord_bot.modules.mod')
logger.warning("modules/mod/__init__.py is deprecated and will be removed in a future version. Use cogs instead.")

from modules.features.mod.reaction_forward.reaction_forward import setup_reaction_forward
from modules.features.mod.link_reaction.link_reaction import setup_link_reaction
from modules.features.mod.keyword_filter.keyword_filter import setup_keyword_filter

__all__ = ["setup_reaction_forward", "setup_link_reaction", "setup_keyword_filter"]

def setup(bot):
    """
    Set up the moderation module.
    
    Args:
        bot: The Discord bot instance
    """
    # Import needed to avoid circular imports
    from discord.ext import commands
    
    logger = logging.getLogger('discord_bot.modules.mod')
    logger.info("Setting up mod module")
    
    # Set up basic ping command
    try:
        @bot.tree.command(name="ping", description="Check if the bot is responsive and view latency")
        async def ping(interaction):
            await interaction.response.send_message("Pong! 🏓")
        logger.info("Registered ping command")
    except Exception as e:
        logger.warning(f"Could not register ping command: {str(e)}")
    
    # Set up purge command
    try:
        from modules.features.mod.general.purge import setup_purge
        setup_purge(bot)
        logger.info("Registered purge command")
    except Exception as e:
        logger.error(f"Failed to set up purge command: {str(e)}")
    
    # Set up pinger feature
    try:
        from modules.features.mod.pinger.pinger import setup_pinger
        setup_pinger(bot)
        logger.info("Set up pinger feature")
        
        # Register pinger-config command
        try:
            from modules.features.mod.pinger.config_cmd import setup_config_cmd as setup_pinger_config
            setup_pinger_config(bot)
            logger.info("Registered pinger-config command")
        except Exception as e:
            logger.warning(f"Could not register pinger-config command: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to set up pinger feature: {str(e)}")
    
    # Set up reaction forward feature
    try:
        setup_reaction_forward(bot)
        logger.info("Set up reaction_forward feature")
        
        # Register reaction-forward-config command
        try:
            from modules.features.mod.reaction_forward.config_cmd import setup_config_cmd as setup_reaction_forward_config
            setup_reaction_forward_config(bot)
            logger.info("Registered reaction-forward-config command")
        except Exception as e:
            logger.warning(f"Could not register reaction-forward-config command: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to set up reaction_forward feature: {str(e)}")
    
    # Set up link reaction feature
    try:
        setup_link_reaction(bot)
        logger.info("Set up link_reaction feature")
        
        # Register link-reaction-config command
        try:
            from modules.features.mod.link_reaction.config_cmd import link_reaction_config
            bot.tree.add_command(link_reaction_config)
            logger.info("Registered link-reaction-config command")
        except Exception as e:
            logger.warning(f"Could not register link-reaction-config command: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to set up link_reaction feature: {str(e)}")
        
    # Set up keyword filter feature
    try:
        setup_keyword_filter(bot)
        logger.info("Set up keyword_filter feature")
        
        # Register keyword-filter-config command
        try:
            from modules.features.mod.keyword_filter.config_cmd import keyword_filter_config
            bot.tree.add_command(keyword_filter_config)
            logger.info("Registered keyword-filter-config command")
        except Exception as e:
            logger.warning(f"Could not register keyword-filter-config command: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to set up keyword_filter feature: {str(e)}")
    
    # Set up mod-config command
    try:
        from modules.features.mod.mod_config_cmd import setup_config_cmd as setup_mod_config
        setup_mod_config(bot)
        logger.info("Registered mod-config command")
    except Exception as e:
        logger.warning(f"Could not register mod-config command: {str(e)}")
