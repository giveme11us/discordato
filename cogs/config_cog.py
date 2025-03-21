"""
Configuration Commands Cog

This cog provides configuration commands for all modules.
"""

import discord
from discord.ext import commands
import logging

# Import module-specific configuration commands
from modules.features.mod.pinger.config_cmd import setup_config_cmd as setup_pinger_config
from modules.features.mod.reaction_forward.config_cmd import setup_config_cmd as setup_reaction_forward_config
from modules.features.mod.link_reaction.config_cmd import link_reaction_config
from modules.features.mod.mod_config_cmd import setup_config_cmd as setup_mod_config

logger = logging.getLogger('discord_bot.cogs.config_cog')

class ConfigCog(commands.Cog):
    """
    Cog for configuration commands.
    """
    
    def __init__(self, bot):
        """
        Initialize the configuration commands cog.
        
        Args:
            bot: The Discord bot instance
        """
        self.bot = bot
        logger.info("Initializing Configuration Commands Cog")
        
        # Register all configuration commands
        try:
            self.bot.tree.add_command(link_reaction_config)
            logger.info("Registered link-reaction-config command")
        except Exception as e:
            logger.error(f"Failed to register link-reaction-config command: {str(e)}")
    
    async def cog_load(self):
        """
        Called when the cog is loaded.
        """
        logger.info("Loading Configuration Commands Cog")
        
        # Setup configuration commands that require more complex initialization
        try:
            setup_pinger_config(self.bot)
            logger.info("Setup pinger-config command")
        except Exception as e:
            logger.error(f"Failed to setup pinger-config command: {str(e)}")
        
        try:
            setup_reaction_forward_config(self.bot)
            logger.info("Setup reaction-forward-config command")
        except Exception as e:
            logger.error(f"Failed to setup reaction-forward-config command: {str(e)}")
        
        try:
            setup_mod_config(self.bot)
            logger.info("Setup mod-config command")
        except Exception as e:
            logger.error(f"Failed to setup mod-config command: {str(e)}")

async def setup(bot):
    """
    Setup function for the configuration commands cog.
    
    Args:
        bot: The Discord bot instance
    """
    await bot.add_cog(ConfigCog(bot))
    logger.info("Configuration Commands Cog added to bot") 