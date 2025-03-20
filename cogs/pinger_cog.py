"""
Pinger Cog

This cog integrates the pinger module with the Discord bot.
"""

import discord
from discord.ext import commands
import logging
from modules.features.mod.pinger.pinger import setup_pinger

logger = logging.getLogger('discord_bot.cogs.pinger_cog')

class PingerCog(commands.Cog):
    """
    Cog for the pinger functionality.
    """
    
    def __init__(self, bot):
        """
        Initialize the pinger cog.
        
        Args:
            bot: The Discord bot instance
        """
        self.bot = bot
        logger.info("Initializing Pinger Cog")
    
    async def cog_load(self):
        """
        Called when the cog is loaded.
        """
        logger.info("Loading Pinger Cog")
        setup_pinger(self.bot)

async def setup(bot):
    """
    Setup function for the pinger cog.
    
    Args:
        bot: The Discord bot instance
    """
    await bot.add_cog(PingerCog(bot))
    logger.info("Pinger Cog added to bot") 