"""
Command Sync

This module handles the synchronization of slash commands with the Discord API.
"""

import logging
import discord
from discord import app_commands
from config import settings
from config.environment import is_development

logger = logging.getLogger('discord_bot.command_sync')

class CommandSync:
    """
    Handles the registration and synchronization of slash commands with Discord.
    """
    
    def __init__(self):
        """
        Initialize the command sync handler.
        """
        self.synced_commands = {}
    
    async def _sync_to_guild(self, bot, guild_id=None):
        """
        Sync commands to a specific guild or globally.
        
        Args:
            bot: The Discord bot instance
            guild_id (int, optional): The guild ID to sync to. If None, syncs globally.
        """
        try:
            # Log the commands that will be synced
            commands = bot.tree.get_commands()
            logger.debug(f"Attempting to sync {len(commands)} commands")
            for cmd in commands:
                logger.debug(f"  - Command: {cmd.name} ({cmd.description})")
            
            if guild_id:
                guild = bot.get_guild(guild_id)
                if not guild:
                    logger.warning(f"Guild with ID {guild_id} not found")
                    return
                
                # Force a clean sync by first copying and clearing commands
                # This is a workaround for Discord's API caching issues
                cmds_copy = bot.tree.get_commands().copy()
                
                try:
                    # Clear all commands from this guild
                    logger.debug(f"Clearing commands from guild {guild.name} ({guild_id})")
                    await bot.tree.sync(guild=guild)
                    
                    # Re-add commands to the tree
                    for cmd in cmds_copy:
                        bot.tree.add_command(cmd, guild=guild)
                    
                    # Now sync the commands again
                    logger.debug(f"Re-syncing commands to guild {guild.name} ({guild_id})")
                    synced = await bot.tree.sync(guild=guild)
                    
                    logger.info(f"Synced {len(synced)} commands to guild {guild.name} ({guild_id})")
                    for cmd in synced:
                        logger.info(f"  - {cmd.name}")
                    
                    return synced
                except Exception as e:
                    logger.error(f"Error during forced sync to guild {guild_id}: {str(e)}")
                    logger.error(f"Falling back to normal sync")
                    
                    # Fall back to normal sync
                    synced = await bot.tree.sync(guild=guild)
                    logger.info(f"Synced {len(synced)} commands to guild {guild.name} ({guild_id})")
                    for cmd in synced:
                        logger.info(f"  - {cmd.name}")
                    
                    return synced
            else:
                # Force sync globally
                synced = await bot.tree.sync()
                logger.info(f"Synced {len(synced)} commands globally")
                for cmd in synced:
                    logger.info(f"  - {cmd.name}")
                
                return synced
        except Exception as e:
            logger.error(f"Error syncing commands: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            return []
    
    def sync_commands(self, bot, bot_name):
        """
        Sync commands for a bot instance.
        
        Args:
            bot: The Discord bot instance
            bot_name (str): The name of the bot
        """
        # Log the commands registered in the bot's command tree
        @bot.event
        async def on_ready():
            logger.info(f"Bot {bot.user.name} is ready")
            
            # Log all registered commands
            cmds = bot.tree.get_commands()
            logger.info(f"Bot has {len(cmds)} registered commands")
            for cmd in cmds:
                logger.info(f"  - Registered command: {cmd.name}")
            
            try:
                # In development mode, sync to development guild
                if is_development() and settings.DEV_GUILD_ID:
                    dev_guild_id = int(settings.DEV_GUILD_ID)
                    await self._sync_to_guild(bot, dev_guild_id)
                else:
                    # In production, sync to specified guilds or globally
                    if hasattr(settings, 'GUILD_IDS') and settings.GUILD_IDS:
                        # Check if GUILD_IDS is a list or a single string (common in environment variables)
                        if isinstance(settings.GUILD_IDS, list):
                            guild_ids = settings.GUILD_IDS
                        else:
                            # If it's a comma-separated string, split it
                            guild_ids = [id.strip() for id in str(settings.GUILD_IDS).split(',') if id.strip()]
                            
                        logger.debug(f"Found guild IDs to sync to: {guild_ids}")
                        
                        for guild_id_str in guild_ids:
                            if guild_id_str:
                                try:
                                    guild_id = int(guild_id_str)
                                    logger.debug(f"Syncing to guild ID: {guild_id}")
                                    await self._sync_to_guild(bot, guild_id)
                                except ValueError:
                                    logger.error(f"Invalid guild ID: {guild_id_str}")
                    else:
                        logger.debug("No guild IDs found, syncing globally")
                        await self._sync_to_guild(bot)
                
                logger.info(f"Command sync completed for {bot_name}")
            except Exception as e:
                logger.error(f"Error during command sync for {bot_name}: {str(e)}")
                
    def register_command(self, bot, command_name, command_callback, description="No description provided", **kwargs):
        """
        Register a slash command with a bot.
        
        Args:
            bot: The Discord bot instance
            command_name (str): The name of the command
            command_callback (callable): The function to call when the command is invoked
            description (str, optional): The description of the command
            **kwargs: Additional arguments for the command
        """
        try:
            @bot.tree.command(name=command_name, description=description, **kwargs)
            async def command(*args, **kwargs):
                return await command_callback(*args, **kwargs)
            
            logger.debug(f"Registered command: {command_name}")
            return True
        except Exception as e:
            logger.error(f"Error registering command {command_name}: {str(e)}")
            return False 