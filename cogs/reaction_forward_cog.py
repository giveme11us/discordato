"""
Reaction Forward Cog

This cog integrates the reaction forward module with the Discord bot.
"""

import discord
from discord.ext import commands
import logging
from modules.mod.reaction_forward import setup_reaction_forward

logger = logging.getLogger('discord_bot.cogs.reaction_forward_cog')

class ReactionForwardCog(commands.Cog):
    """
    Cog for the reaction forward functionality.
    """
    
    def __init__(self, bot):
        """
        Initialize the reaction forward cog.
        
        Args:
            bot: The Discord bot instance
        """
        self.bot = bot
        logger.info("Initializing Reaction Forward Cog")
    
    async def cog_load(self):
        """
        Called when the cog is loaded.
        """
        logger.info("Loading Reaction Forward Cog")
        setup_reaction_forward(self.bot)

async def setup(bot):
    """
    Setup function for the reaction forward cog.
    
    Args:
        bot: The Discord bot instance
    """
    await bot.add_cog(ReactionForwardCog(bot))
    logger.info("Reaction Forward Cog added to bot") 