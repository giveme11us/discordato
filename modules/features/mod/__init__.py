"""
Moderation features module
"""

import logging
from modules.features.mod.reaction_forward.reaction_forward import setup_reaction_forward
from modules.features.mod.link_reaction.link_reaction import setup_link_reaction

logger = logging.getLogger('discord_bot.features.mod')

__all__ = ["setup_reaction_forward", "setup_link_reaction"]

async def setup(bot):
    """
    Set up all moderation features.
    
    Args:
        bot: The Discord bot instance
    """
    logger.info("Setting up moderation features")
    
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
    
    logger.info("Finished setting up moderation features")
