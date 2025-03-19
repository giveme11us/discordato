"""
Link Reaction Cog

This cog integrates the link reaction module with the Discord bot.
"""

import discord
from discord.ext import commands
import logging
from modules.mod.link_reaction import setup_link_reaction

logger = logging.getLogger('discord_bot.cogs.link_reaction_cog')

class LinkReactionCog(commands.Cog):
    """
    Cog for the link reaction functionality.
    """
    
    def __init__(self, bot):
        """
        Initialize the link reaction cog.
        
        Args:
            bot: The Discord bot instance
        """
        self.bot = bot
        logger.info("Initializing Link Reaction Cog")
    
    async def cog_load(self):
        """
        Called when the cog is loaded.
        """
        logger.info("Loading Link Reaction Cog")
        setup_link_reaction(self.bot)

async def setup(bot):
    """
    Setup function for the link reaction cog.
    
    Args:
        bot: The Discord bot instance
    """
    await bot.add_cog(LinkReactionCog(bot))
    logger.info("Link Reaction Cog added to bot") 