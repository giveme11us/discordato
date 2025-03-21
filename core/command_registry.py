"""
Command Registry

This module provides a central registry for managing Discord bot commands.

The Command Registry is responsible for:
1. Registering and tracking bot commands
2. Preventing duplicate command registration
3. Managing command metadata and permissions
4. Synchronizing commands with Discord
5. Caching command states
6. Batching command updates
7. Rate limiting command operations

Critical:
- Commands must have unique names
- Commands must be registered before syncing
- Command metadata must be complete
- Permissions must be properly configured
- Must handle rate limits
- Should use caching
- Must batch updates
"""

import logging
import discord
from discord import app_commands
from typing import Dict, Set, Optional, List, Any
from datetime import datetime, timedelta
from .commands.base import BaseCommand
from .commands.permission_commands import permission_commands
from .command_sync import command_sync
from .error_handler import CommandError
import asyncio

logger = logging.getLogger('discord_bot.command_registry')

class CommandRegistry:
    """
    Central registry for managing Discord bot commands.
    
    This class handles:
    - Command registration and tracking
    - Command metadata management
    - Discord command synchronization
    - Permission configuration
    - Command state caching
    - Batched updates
    - Rate limiting
    
    Attributes:
        _commands (Dict[str, BaseCommand]): Maps command names to instances
        _registered_commands (Set[str]): Set of synced command names
        command_groups (Dict[str, List[BaseCommand]]): Dictionary of command group names to commands
        _command_cache (Dict[str, Any]): Cache for command metadata
        _last_sync (datetime): Timestamp of last sync operation
        _pending_syncs (Set[str]): Set of commands pending sync
        
    Critical:
        - Command names must be unique
        - Commands must be properly configured
        - Permissions must be validated
        - Sync state must be tracked
    """
    
    def __init__(self):
        """
        Initialize the command registry.
        
        Sets up:
        - Command storage collections
        - Registration tracking
        - Sync state management
        """
        self._commands: Dict[str, BaseCommand] = {}
        self._registered_commands: Set[str] = set()
        self.command_groups: Dict[str, List[BaseCommand]] = {}
        self._command_cache: Dict[str, Any] = {}
        self._last_sync = datetime.min
        self._pending_syncs: Set[str] = set()
        
    def register_command(self, command: BaseCommand, group: str = None) -> None:
        """
        Register a command with the registry.
        
        Args:
            command: The command to register
            group: Optional group name for the command
            
        Raises:
            ValueError: If command name is already registered
        """
        if command.name in self._commands:
            raise ValueError(f"Command {command.name} is already registered")
            
        self._commands[command.name] = command
        self._registered_commands.add(command.name)
        self._pending_syncs.add(command.name)
        
        # Cache command metadata
        self._command_cache[command.name] = {
            'name': command.name,
            'description': command.description,
            'permissions': command.permissions,
            'group': group,
            'registered_at': datetime.now()
        }
        
        if group:
            if group not in self.command_groups:
                self.command_groups[group] = []
            self.command_groups[group].append(command)
            
        logger.info(f"Registered command: {command.name} in group: {group}")
        
    def register_commands(self, commands: List[BaseCommand], group: str = None) -> None:
        """
        Register multiple commands at once.
        
        Args:
            commands: List of commands to register
            group: Optional group name for the commands
        """
        for command in commands:
            self.register_command(command, group)
        
    def get_command(self, name: str) -> Optional[BaseCommand]:
        """
        Retrieve a registered command by name.
        
        Args:
            name (str): Name of the command to retrieve
            
        Returns:
            Optional[BaseCommand]: Command instance if found, None otherwise
            
        Note:
            Checks cache first before accessing storage
        """
        # Check cache first
        if name in self._command_cache:
            cached = self._command_cache[name]
            if 'instance' in cached:
                return cached['instance']
                
        command = self._commands.get(name)
        if command:
            # Update cache
            if name in self._command_cache:
                self._command_cache[name]['instance'] = command
            else:
                self._command_cache[name] = {
                    'name': command.name,
                    'description': command.description,
                    'permissions': command.permissions,
                    'instance': command
                }
        return command
        
    async def register_with_bot(self, bot: discord.Client) -> None:
        """
        Register all commands with the Discord bot.
        
        This method:
        1. Converts commands to Discord format
        2. Registers with Discord's command system
        3. Updates sync state tracking
        4. Handles rate limits
        5. Batches updates
        
        Args:
            bot (discord.Client): The Discord bot instance
            
        Note:
            Uses command_sync for optimized registration
        """
        try:
            # Register commands in batches
            batch_size = 25
            commands = list(self._commands.values())
            
            for i in range(0, len(commands), batch_size):
                batch = commands[i:i + batch_size]
                for command in batch:
                    if command.name in self._pending_syncs:
                        app_command = command.to_app_command()
                        success = await command_sync.register_command(
                            bot=bot,
                            command_name=command.name,
                            command_callback=app_command.callback,
                            description=command.description,
                            **command.options
                        )
                        if success:
                            self._pending_syncs.remove(command.name)
                            
                # Small delay between batches to avoid rate limits
                if i + batch_size < len(commands):
                    await asyncio.sleep(1)
                    
            # Sync commands if needed
            if self._pending_syncs:
                await command_sync.sync_commands(bot)
                self._pending_syncs.clear()
                
            logger.info("Successfully registered all commands with Discord")
            
        except Exception as e:
            logger.error(f"Failed to register commands: {e}", exc_info=True)
            raise CommandError(f"Failed to register commands: {str(e)}")
            
    @property
    def registered_commands(self) -> Set[str]:
        """
        Get the set of registered command names.
        
        Returns:
            Set[str]: Copy of registered command names
            
        Note:
            Returns a copy to prevent external modification
        """
        return self._registered_commands.copy()
        
    def __len__(self) -> int:
        """
        Get the number of registered commands.
        
        Returns:
            int: Total number of registered commands
        """
        return len(self._commands)
        
    def __iter__(self):
        """
        Iterate over registered commands.
        
        Yields:
            BaseCommand: Each registered command instance
        """
        return iter(self._commands.values())

    def clear_cache(self) -> None:
        """Clear the command cache."""
        self._command_cache.clear()
        logger.info("Command cache cleared")
        
    async def setup_commands(self, tree: app_commands.CommandTree) -> None:
        """
        Set up all registered commands with the Discord command tree.
        
        Args:
            tree: The Discord command tree
            
        Note:
            Uses batching and rate limiting for optimal performance
        """
        try:
            # Register ungrouped commands first
            ungrouped = self.command_groups.get(None, [])
            for i in range(0, len(ungrouped), 25):
                batch = ungrouped[i:i + 25]
                for command in batch:
                    command.register(tree)
                if i + 25 < len(ungrouped):
                    await asyncio.sleep(1)
                    
            # Then register grouped commands
            for group_name, commands in self.command_groups.items():
                if group_name:
                    for i in range(0, len(commands), 25):
                        batch = commands[i:i + 25]
                        for command in batch:
                            command.register(tree)
                        if i + 25 < len(commands):
                            await asyncio.sleep(1)
                            
            logger.info("All commands have been set up")
            
        except Exception as e:
            logger.error(f"Failed to set up commands: {e}", exc_info=True)
            raise CommandError(f"Failed to set up commands: {str(e)}")

# Global command registry instance
command_registry = CommandRegistry()

def register_all_commands(bot: discord.Client) -> None:
    """
    Register all commands with the Discord bot.
    
    This function:
    1. Registers utility commands
    2. Registers configuration commands
    3. Registers moderation commands
    
    Args:
        bot (discord.Client): The Discord bot instance
        
    Note:
        Commands must be registered before syncing with Discord
    """
    logger.info("Registering all commands centrally")
    registered_count = 0
    registered_commands = []
    
    try:
        # Register utility commands
        @bot.tree.command(
            name="ping",
            description="Check if the bot is responsive and view latency"
        )
        async def ping(interaction: discord.Interaction):
            """
            Check bot responsiveness and latency.
            
            This command:
            1. Measures response time
            2. Calculates latency
            3. Returns results to user
            
            Args:
                interaction (discord.Interaction): Command interaction
            """
            import time
            start_time = time.time()
            await interaction.response.defer(ephemeral=False)
            end_time = time.time()
            
            latency = round((end_time - start_time) * 1000)
            await interaction.followup.send(f"Pong! 🏓 Latency: {latency}ms")
            logger.debug(f"Ping command executed by {interaction.user} with latency {latency}ms")
        
        registered_commands.append("ping")
        registered_count += 1
        
        @bot.tree.command(
            name="hi",
            description="Get a friendly greeting from the bot"
        )
        async def hi(interaction: discord.Interaction):
            """
            Send a friendly greeting to the user.
            
            This command:
            1. Selects a random greeting
            2. Personalizes it for the user
            3. Sends the response
            
            Args:
                interaction (discord.Interaction): Command interaction
            """
            import random
            greetings = [
                "Hello there, {}! How are you doing today?",
                "Hi, {}! Nice to see you!",
                "Hey {}! What's up?",
                "Greetings, {}! How can I assist you today?",
                "Hi there {}! Hope you're having a great day!"
            ]
            greeting = random.choice(greetings).format(interaction.user.display_name)
            await interaction.response.send_message(greeting)
            logger.debug(f"Hi command executed by {interaction.user}")
        
        registered_commands.append("hi")
        registered_count += 1
        
        @bot.tree.command(
            name="number",
            description="Generate a random number within a specified range"
        )
        @app_commands.describe(
            min_value="The minimum value (default: 1)",
            max_value="The maximum value (default: 100)"
        )
        async def number(interaction: discord.Interaction, min_value: int = 1, max_value: int = 100):
            """
            Generate a random number in a range.
            
            This command:
            1. Validates input range
            2. Generates random number
            3. Returns formatted result
            
            Args:
                interaction (discord.Interaction): Command interaction
                min_value (int, optional): Minimum value (default: 1)
                max_value (int, optional): Maximum value (default: 100)
            """
            import random
            if min_value >= max_value:
                await interaction.response.send_message(
                    "Error: Minimum value must be less than maximum value.",
                    ephemeral=True
                )
                return
            
            number = random.randint(min_value, max_value)
            await interaction.response.send_message(
                f"🎲 Your random number between {min_value} and {max_value} is: **{number}**"
            )
            logger.debug(f"Number command executed by {interaction.user}")
        
        # Register configuration commands
        @bot.tree.command(
            name="pinger-config",
            description="Configure the pinger feature"
        )
        @app_commands.describe(
            setting="The setting to view or modify (channel, whitelist, everyone, here)",
            value="The new value for the setting"
        )
        @app_commands.choices(
            setting=[
                app_commands.Choice(name="View Current Configuration", value="view"),
                app_commands.Choice(name="Notification Channel", value="channel"),
                app_commands.Choice(name="Whitelist Roles", value="whitelist"),
                app_commands.Choice(name="@everyone Mentions", value="everyone"),
                app_commands.Choice(name="@here Mentions", value="here")
            ]
        )
        async def pinger_config(interaction: discord.Interaction, setting: str = None, value: str = None):
            """
            Configure pinger feature settings.
            
            This command:
            1. Validates user permissions
            2. Processes configuration changes
            3. Updates settings
            
            Args:
                interaction (discord.Interaction): Command interaction
                setting (str, optional): Setting to modify
                value (str, optional): New setting value
                
            Note:
                Requires administrator permissions
            """
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "You need administrator permissions to use this command.",
                    ephemeral=True
                )
                return
            
            try:
                from modules.mod.pinger.config_cmd import config_command
                await config_command(interaction, setting, value)
            except Exception as e:
                logger.error(f"Error executing pinger-config command: {str(e)}")
                await interaction.response.send_message(
                    "An error occurred while executing the command.",
                    ephemeral=True
                )
            
            logger.debug(f"Pinger-config command executed by {interaction.user}")
        
        registered_commands.append("pinger-config")
        registered_count += 1
    except Exception as e:
        logger.error(f"Error registering utility commands: {e}")
    
    try:
        # Register purge command
        @bot.tree.command(
            name="purge",
            description="Delete a specified number of messages in the current channel"
        )
        @app_commands.describe(
            count="The number of messages to delete (max 100)"
        )
        async def purge(interaction: discord.Interaction, count: int = 10):
            """
            Delete multiple messages in the current channel.
            
            This command:
            1. Validates user permissions
            2. Validates message count
            3. Deletes messages
            
            Args:
                interaction (discord.Interaction): Command interaction
                count (int, optional): Number of messages to delete (default: 10)
                
            Note:
                Requires manage messages permission
                Maximum of 100 messages can be deleted at once
            """
            if not interaction.user.guild_permissions.manage_messages:
                await interaction.response.send_message(
                    "You need manage messages permission to use this command.",
                    ephemeral=True
                )
                return
            
            if count < 1 or count > 100:
                await interaction.response.send_message(
                    "Please specify a number between 1 and 100.",
                    ephemeral=True
                )
                return
            
            try:
                await interaction.response.defer(ephemeral=True)
                deleted = await interaction.channel.purge(limit=count)
                await interaction.followup.send(
                    f"Successfully deleted {len(deleted)} messages.",
                    ephemeral=True
                )
                logger.info(f"Purged {len(deleted)} messages in {interaction.channel.name} by {interaction.user}")
            except Exception as e:
                logger.error(f"Error executing purge command: {str(e)}")
                await interaction.followup.send(
                    "An error occurred while deleting messages.",
                    ephemeral=True
                )
            
            logger.debug(f"Purge command executed by {interaction.user}")
        
        registered_commands.append("purge")
        registered_count += 1
    except Exception as e:
        logger.error(f"Error registering purge command: {e}")
    
    logger.info(f"Registered {registered_count} commands centrally")
    for cmd in registered_commands:
        logger.info(f"  - Registered command: {cmd}")
    
    return registered_count