"""
Keyword Filter Cog

This cog integrates the keyword filter module with the Discord bot.
"""

import discord
from discord.ext import commands
import logging
from modules.features.mod.keyword_filter import setup_keyword_filter

logger = logging.getLogger('discord_bot.cogs.keyword_filter_cog')

class KeywordFilterCog(commands.Cog):
    """
    Cog for the keyword filter functionality.
    """
    
    def __init__(self, bot):
        """
        Initialize the keyword filter cog.
        
        Args:
            bot: The Discord bot instance
        """
        self.bot = bot
        logger.info("Initializing Keyword Filter Cog")
    
    async def cog_load(self):
        """
        Called when the cog is loaded.
        """
        logger.info("Loading Keyword Filter Cog")
        setup_keyword_filter(self.bot)

async def setup(bot):
    """
    Setup function for the keyword filter cog.
    
    Args:
        bot: The Discord bot instance
    """
    await bot.add_cog(KeywordFilterCog(bot))
    logger.info("Keyword Filter Cog added to bot") 