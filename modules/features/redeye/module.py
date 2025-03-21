"""
Redeye Module

Module for handling Redeye functionality.
"""

import logging
from typing import Optional, Set
from discord.ext import commands
from .profile_cmd import setup_profile_cmd
from .help_cmd import setup_help_cmd
from config.features.redeye_config import redeye as redeye_config

logger = logging.getLogger('discord_bot.modules.redeye')

async def setup(bot: commands.Bot, registered_commands: Optional[Set[str]] = None) -> Set[str]:
    """
    Set up the Redeye module.
    
    Args:
        bot: The Discord bot instance
        registered_commands: Set of registered command names
    
    Returns:
        Set of registered command names
    """
    try:
        logger.info("Setting up Redeye module")
        
        # Initialize registered_commands if not provided
        if registered_commands is None:
            registered_commands = set()
        
        # Log commands before clearing
        logger.info("=== Commands Before Clearing ===")
        for cmd in bot.tree.get_commands():
            logger.info(f"Command: /{cmd.name}")
            if hasattr(cmd, 'commands'):
                for subcmd in cmd.commands:
                    logger.info(f"  ├─ /{cmd.name} {subcmd.name}")
                    if hasattr(subcmd, 'commands'):
                        for nested_cmd in subcmd.commands:
                            logger.info(f"  │  └─ /{cmd.name} {subcmd.name} {nested_cmd.name}")
        logger.info("=============================")
        
        # Clear any existing redeye commands
        existing_commands = bot.tree.get_commands()
        for cmd in existing_commands:
            if cmd.name in ['redeye', 'redeye_help']:
                bot.tree.remove_command(cmd.name)
                if cmd.name in registered_commands:
                    registered_commands.remove(cmd.name)
        
        # Set up profile commands
        registered_commands = await setup_profile_cmd(bot, registered_commands)
        
        logger.info("Redeye module setup complete")
        return registered_commands
        
    except Exception as e:
        logger.error(f"Error setting up Redeye module: {e}", exc_info=True)
        return registered_commands

async def teardown(bot: commands.Bot):
    """
    Clean up the Redeye module.
    
    Args:
        bot: The Discord bot instance
    """
    logger.info("Tearing down Redeye module")

# Expose setup function directly
__all__ = ['setup', 'teardown'] 