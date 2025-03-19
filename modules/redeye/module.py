"""
Redeye Module (Legacy Format)

This is the main entry point for the redeye module in the legacy module format.
This format is being phased out in favor of a cog-based architecture.
"""

import logging
import discord
from discord.ext import commands
from modules.redeye.redeye import setup_redeye
from modules.redeye.config_cmd import setup_config_cmd
from config import redeye_config

logger = logging.getLogger('discord_bot.modules.redeye.module')

def setup(bot, registered_commands=None):
    """
    Set up the redeye module.
    
    Args:
        bot: The Discord bot instance
        registered_commands: Optional set of commands that are already registered
    """
    logger.info("Setting up redeye module (legacy format)")
    
    # Directly access settings from the settings_manager to avoid property issues
    enabled = redeye_config.settings_manager.get("ENABLED", False)
    waitlists = redeye_config.settings_manager.get("WAITLISTS", {})
    role_requirements = redeye_config.settings_manager.get("ROLE_REQUIREMENTS", {})
    notification_channel = redeye_config.settings_manager.get("NOTIFICATION_CHANNEL_ID", None)
    status_emojis = redeye_config.settings_manager.get("STATUS_EMOJIS", {})
    
    logger.info(f"Current settings - Enabled: {enabled}, Waitlists: {len(waitlists)}, Role requirements: {len(role_requirements)}")
    
    # Set up the redeye functionality
    try:
        setup_redeye(bot)
        logger.info("Redeye core functionality set up successfully")
    except Exception as e:
        logger.error(f"Error setting up redeye core functionality: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Register the config command
    try:
        setup_config_cmd(bot)
        logger.info("Redeye config command registered successfully")
    except Exception as e:
        logger.error(f"Error registering redeye config command: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    logger.info("Redeye module setup complete")

def teardown(bot):
    """
    Clean up the redeye module when unloaded.
    
    Args:
        bot: The Discord bot instance
    """
    logger.info("Tearing down redeye module")
    
    # Remove event listeners if needed
    # This is empty for now since we don't have persistent resources to clean up 