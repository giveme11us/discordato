"""
RedEye Module

This module provides functionality for RedEye-specific features.
"""

import logging
from modules.features.redeye.profile_cmd import setup_profile_cmd

logger = logging.getLogger('discord_bot.modules.redeye')

def setup(bot):
    """
    Set up the RedEye module.
    
    Args:
        bot: The Discord bot instance
    """
    logger.info("Setting up RedEye module")
    
    # Set up profile command
    setup_profile_cmd(bot)
    
    logger.info("Successfully set up RedEye module")

__all__ = ["setup_profile_cmd"] 