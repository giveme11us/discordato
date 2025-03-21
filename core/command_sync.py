"""
Command Sync

This module handles the synchronization of slash commands with the Discord API.

The CommandSync module is responsible for:
1. Registering and managing slash commands
2. Synchronizing commands across guilds and globally
3. Handling command permissions and rate limits
4. Managing command lifecycle and updates
5. Ensuring command consistency across environments
6. Tracking command registration state
7. Managing command versioning

Critical:
- Must handle rate limits appropriately
- Should sync commands during bot initialization
- Must maintain proper command permissions
- Should handle both global and guild-specific commands
- Must ensure atomic command updates
- Should track command registration state
- Must validate command configurations
- Should support command versioning
- Must handle sync failures gracefully

Classes:
    CommandSync: Main class for managing Discord slash commands
"""

import logging
import discord
import asyncio
from typing import Dict, List, Optional, Set, Tuple
from discord import app_commands
from datetime import datetime, timedelta
from config.core.settings import settings
from config.environment.environment import is_development
from core.error_handler import CommandError

logger = logging.getLogger('discord_bot.command_sync')

# Constants for rate limit handling
SYNC_COOLDOWN = 60  # Minimum seconds between syncs
RETRY_BUFFER = 10.0  # Buffer to add to rate limit times
MAX_RETRIES = 3
BATCH_SIZE = 25
CACHE_TTL = 3600  # Cache time-to-live in seconds

class CommandSync:
    """
    Manages the registration and synchronization of Discord slash commands.
    
    This class provides:
    1. Command registration and deregistration with caching
    2. Global and guild-specific command syncing
    3. Command permission management
    4. Rate limit handling and retries
    5. Command state tracking
    6. Version management
    7. Sync failure recovery
    8. Batched command updates
    
    Attributes:
        _command_cache (Dict[str, Tuple[app_commands.Command, datetime]]): Cache of registered commands with timestamps
        _last_sync (Dict[int, datetime]): Last sync time per guild
        _sync_queue (Set[str]): Queue of commands pending sync
        _guild_sync_states (Dict[int, bool]): Sync state per guild
        _global_sync_state (bool): Global sync state
        _sync_lock (asyncio.Lock): Lock for synchronization operations
        _rate_limit_data (Dict[str, Dict]): Rate limit tracking per endpoint
    """
    
    def __init__(self):
        """Initialize the command synchronization system."""
        self._command_cache = {}  # Now stores (command, timestamp) tuples
        self._last_sync = {}
        self._sync_queue = set()
        self._guild_sync_states = {}
        self._global_sync_state = False
        self._sync_lock = asyncio.Lock()
        self._rate_limit_data = {}
        
    def _can_sync(self, guild_id: Optional[int] = None) -> bool:
        """
        Check if sync is allowed based on cooldown and rate limits.
        
        Args:
            guild_id: Optional guild ID to check
            
        Returns:
            bool: True if sync is allowed
        """
        now = datetime.now()
        
        # Check cooldown
        last_sync = self._last_sync.get(guild_id, datetime.min)
        if (now - last_sync).total_seconds() < SYNC_COOLDOWN:
            return False
            
        # Check rate limits
        endpoint = f"sync_{guild_id if guild_id else 'global'}"
        rate_limit = self._rate_limit_data.get(endpoint, {})
        if rate_limit:
            reset_time = rate_limit.get('reset_at', datetime.min)
            if now < reset_time:
                return False
                
        return True
        
    def _update_rate_limit(self, endpoint: str, reset_after: float) -> None:
        """Update rate limit data for an endpoint."""
        self._rate_limit_data[endpoint] = {
            'reset_at': datetime.now() + timedelta(seconds=reset_after),
            'remaining': 0
        }
        
    def _is_cache_valid(self, command_name: str) -> bool:
        """Check if a cached command is still valid."""
        if command_name not in self._command_cache:
            return False
            
        _, timestamp = self._command_cache[command_name]
        return (datetime.now() - timestamp).total_seconds() < CACHE_TTL
        
    async def _batch_sync(self, bot: discord.Client, commands: List[app_commands.Command],
                         guild_id: Optional[int] = None) -> None:
        """
        Sync commands in batches to avoid rate limits.
        
        Args:
            bot: Discord bot instance
            commands: List of commands to sync
            guild_id: Optional guild ID for guild-specific sync
        """
        endpoint = f"sync_{guild_id if guild_id else 'global'}"
        
        for i in range(0, len(commands), BATCH_SIZE):
            batch = commands[i:i + BATCH_SIZE]
            guild = discord.Object(id=guild_id) if guild_id else None
            
            for attempt in range(MAX_RETRIES):
                try:
                    await bot.tree.sync(guild=guild)
                    break
                except discord.HTTPException as e:
                    if isinstance(e, discord.RateLimited):
                        self._update_rate_limit(endpoint, e.retry_after)
                        wait_time = e.retry_after + RETRY_BUFFER
                    else:
                        wait_time = (attempt + 1) * RETRY_BUFFER
                        
                    if attempt == MAX_RETRIES - 1:
                        raise CommandError(f"Failed to sync command batch after {MAX_RETRIES} attempts")
                        
                    logger.warning(f"Sync attempt {attempt + 1} failed, waiting {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                    
            await asyncio.sleep(1)  # Small delay between batches
            
    async def sync_commands(self, bot: discord.Client, guild_id: Optional[int] = None) -> None:
        """
        Synchronize commands with Discord.
        
        Args:
            bot: Discord bot instance
            guild_id: Optional guild ID for guild-specific sync
        """
        async with self._sync_lock:
            if not self._can_sync(guild_id):
                logger.info(f"Sync cooldown or rate limit active for guild {guild_id}")
                return
                
            try:
                # Filter out invalid cache entries
                valid_commands = [
                    cmd for name, (cmd, _) in self._command_cache.items()
                    if self._is_cache_valid(name)
                ]
                
                await self._batch_sync(bot, valid_commands, guild_id)
                self._update_sync_time(guild_id)
                
                if guild_id:
                    self._guild_sync_states[guild_id] = True
                else:
                    self._global_sync_state = True
                    
                logger.info(f"Successfully synced {len(valid_commands)} commands" + 
                          f" for guild {guild_id}" if guild_id else " globally")
                          
            except Exception as e:
                logger.error(f"Failed to sync commands: {e}", exc_info=True)
                raise CommandError(f"Failed to sync commands: {str(e)}")
                
    def register_command(self, bot: discord.Client, command_name: str,
                        command_callback: callable, description: str = "No description provided",
                        **kwargs) -> bool:
        """
        Register a slash command with caching.
        
        Args:
            bot: Discord bot instance
            command_name: Name of the command
            command_callback: Command handler function
            description: Command description
            **kwargs: Additional command options
            
        Returns:
            bool: True if registration successful
        """
        try:
            # Check cache first
            if command_name in self._command_cache and self._is_cache_valid(command_name):
                logger.debug(f"Using cached command {command_name}")
                return True
                
            @bot.tree.command(name=command_name, description=description, **kwargs)
            async def command(interaction: discord.Interaction, **params):
                return await command_callback(interaction, **params)
                
            # Cache the command with timestamp
            self._command_cache[command_name] = (command, datetime.now())
            self._sync_queue.add(command_name)
            
            logger.debug(f"Registered command: {command_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering command {command_name}: {str(e)}")
            return False
            
    def get_command(self, command_name: str) -> Optional[app_commands.Command]:
        """
        Get a command from cache.
        
        Args:
            command_name: Name of the command
            
        Returns:
            Optional[app_commands.Command]: Cached command or None
        """
        if command_name in self._command_cache and self._is_cache_valid(command_name):
            command, _ = self._command_cache[command_name]
            return command
        return None
        
    def clear_cache(self) -> None:
        """Clear the command cache."""
        self._command_cache.clear()
        self._sync_queue.clear()
        logger.info("Command cache cleared")
        
    def is_synced(self, guild_id: Optional[int] = None) -> bool:
        """
        Check if commands are synced.
        
        Args:
            guild_id: Optional guild ID to check
            
        Returns:
            bool: True if commands are synced
        """
        return self._guild_sync_states.get(guild_id, False) if guild_id else self._global_sync_state
        
    async def setup_commands(self, bot: discord.Client) -> None:
        """
        Set up all commands during bot initialization.
        
        Args:
            bot: Discord bot instance
        """
        try:
            # For development, sync to specific guilds
            if is_development():
                guild_ids = settings.GUILD_IDS
                if guild_ids:
                    for guild_id in guild_ids:
                        guild = bot.get_guild(guild_id)
                        if guild:
                            logger.info(f"Syncing commands for guild: {guild.name}")
                            await self.sync_commands(bot, guild_id)
                        else:
                            logger.warning(f"Could not find guild with ID {guild_id}")
                            
            # Always sync globally for production
            await self.sync_commands(bot)
            
        except Exception as e:
            logger.error(f"Error setting up commands: {e}", exc_info=True)
            raise CommandError(f"Failed to set up commands: {str(e)}")

# Global command sync instance
command_sync = CommandSync()