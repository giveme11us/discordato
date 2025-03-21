"""
Command Registry

This module provides a central registry for managing Discord bot commands.

The Command Registry is responsible for:
1. Registering and tracking bot commands
2. Preventing duplicate command registration
3. Managing command metadata and permissions
4. Synchronizing commands with Discord

Critical:
- Commands must have unique names
- Commands must be registered before syncing
- Command metadata must be complete
- Permissions must be properly configured

Classes:
    CommandRegistry: Central registry for managing bot commands
    BaseCommand: Base class for all commands
"""

import logging
import discord
from discord import app_commands
from typing import Dict, Set, Optional
from .commands.base import BaseCommand

logger = logging.getLogger('discord_bot.command_registry')

class CommandRegistry:
    """
    Central registry for managing Discord bot commands.
    
    This class handles:
    - Command registration and tracking
    - Command metadata management
    - Discord command synchronization
    - Permission configuration
    
    Attributes:
        _commands (Dict[str, BaseCommand]): Maps command names to instances
        _registered_commands (Set[str]): Set of synced command names
        
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
        
    def register_command(self, command: BaseCommand) -> None:
        """
        Register a new command in the registry.
        
        This method:
        1. Validates command uniqueness
        2. Stores command instance
        3. Tracks registration state
        
        Args:
            command (BaseCommand): Command instance to register
            
        Raises:
            ValueError: If command name is already registered
            
        Note:
            Commands must be registered before syncing with Discord
        """
        if command.name in self._commands:
            raise ValueError(f"Command '{command.name}' is already registered")
            
        self._commands[command.name] = command
        logger.info(f"Registered command: {command.name}")
        
    def get_command(self, name: str) -> Optional[BaseCommand]:
        """
        Retrieve a registered command by name.
        
        Args:
            name (str): Name of the command to retrieve
            
        Returns:
            Optional[BaseCommand]: Command instance if found, None otherwise
            
        Note:
            Returns None if command is not registered
        """
        return self._commands.get(name)
        
    def register_with_bot(self, bot: discord.Client) -> None:
        """
        Register all commands with the Discord bot.
        
        This method:
        1. Converts commands to Discord format
        2. Registers with Discord's command system
        3. Updates sync state tracking
        
        Args:
            bot (discord.Client): The Discord bot instance
            
        Note:
            Failures are logged but don't stop registration
        """
        for command in self._commands.values():
            try:
                app_command = command.to_app_command()
                bot.tree.add_command(app_command)
                self._registered_commands.add(command.name)
                logger.info(f"Registered command with Discord: {command.name}")
            except Exception as e:
                logger.error(f"Failed to register command {command.name}: {e}")
                
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

# Global registry instance
registry = CommandRegistry()

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
        # Register keyword-filter-config command
        @bot.tree.command(
            name="keyword-filter-config",
            description="Configure the keyword filter feature"
        )
        @app_commands.describe(
            action="The action to perform (view, enable, disable, categories, blacklist, filters, dry_run)",
            filter_id="The filter ID to configure (for filters action)",
            setting="The setting to modify for the selected filter or feature",
            value="The new value for the setting"
        )
        @app_commands.choices(
            action=[
                app_commands.Choice(name="View Configuration", value="view"),
                app_commands.Choice(name="Enable Feature", value="enable"),
                app_commands.Choice(name="Disable Feature", value="disable"),
                app_commands.Choice(name="Manage Categories", value="categories"),
                app_commands.Choice(name="Manage Blacklist", value="blacklist"),
                app_commands.Choice(name="Configure Notifications", value="notification"),
                app_commands.Choice(name="Toggle Dry Run Mode", value="dry_run"),
                app_commands.Choice(name="Manage Filters", value="filters")
            ]
        )
        async def keyword_filter_config(
            interaction: discord.Interaction, 
            action: str = "view",
            filter_id: str = None,
            setting: str = None,
            value: str = None
        ):
            """
            Configure keyword filter feature settings.
            
            This command:
            1. Validates user permissions
            2. Processes configuration changes
            3. Updates filter settings
            
            Args:
                interaction (discord.Interaction): Command interaction
                action (str, optional): Action to perform (default: view)
                filter_id (str, optional): Filter ID to configure
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
                from modules.mod.keyword_filter.config_cmd import keyword_filter_config
                await keyword_filter_config.callback(interaction, action, filter_id, setting, value)
            except Exception as e:
                logger.error(f"Error executing keyword-filter-config command: {str(e)}")
                await interaction.response.send_message(
                    "An error occurred while executing the command.",
                    ephemeral=True
                )
            
            logger.debug(f"Keyword-filter-config command executed by {interaction.user}")
        
        registered_commands.append("keyword-filter-config")
        registered_count += 1
    except Exception as e:
        logger.error(f"Error registering keyword-filter-config command: {e}")
    
    try:
        # Register keyword-filter-quicksetup command
        @bot.tree.command(
            name="keyword-filter-quicksetup",
            description="Quick setup for keyword filter with a single command"
        )
        @app_commands.describe(
            source_channel="The channel or category ID to monitor for keywords",
            notification_channel="The channel ID where notifications will be sent",
            keywords="Comma-separated list of keywords to filter (e.g., 'test,hello,example')"
        )
        async def keyword_filter_quicksetup(
            interaction: discord.Interaction,
            source_channel: str,
            notification_channel: str,
            keywords: str
        ):
            """
            Quick setup for keyword filter with a single command.
            
            This command:
            1. Validates user permissions
            2. Processes setup request
            3. Updates settings
            
            Args:
                interaction (discord.Interaction): Command interaction
                source_channel (str): Channel or category ID to monitor for keywords
                notification_channel (str): Channel ID where notifications will be sent
                keywords (str): Comma-separated list of keywords to filter
                
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
                from modules.mod.keyword_filter.config_cmd import keyword_filter_quicksetup
                # Access the command's callback function instead of calling the command object directly
                await keyword_filter_quicksetup.callback(interaction, source_channel, notification_channel, keywords)
            except Exception as e:
                logger.error(f"Error executing keyword-filter-quicksetup command: {str(e)}")
                await interaction.response.send_message(
                    "An error occurred while executing the command.",
                    ephemeral=True
                )
            
            logger.debug(f"Keyword-filter-quicksetup command executed by {interaction.user}")
        
        registered_commands.append("keyword-filter-quicksetup")
    except Exception as e:
        logger.error(f"Error registering keyword-filter-quicksetup command: {e}")
    
    try:
        # Register reaction-forward-config command
        @bot.tree.command(
            name="reaction-forward-config",
            description="Configure the reaction forward feature"
        )
        @app_commands.describe(
            setting="The setting to view or modify (categories, enable, disable, forwarding, blacklist)",
            value="The new value for the setting"
        )
        @app_commands.choices(
            setting=[
                app_commands.Choice(name="View Configuration", value="view"),
                app_commands.Choice(name="Enable Feature", value="enable"),
                app_commands.Choice(name="Disable Feature", value="disable"),
                app_commands.Choice(name="Toggle Forwarding", value="forwarding"),
                app_commands.Choice(name="Manage Categories", value="categories"),
                app_commands.Choice(name="Manage Blacklist", value="blacklist")
            ]
        )
        async def reaction_forward_config(interaction: discord.Interaction, setting: str = "view", value: str = None):
            """
            Configure reaction forwarding settings.
            
            This command:
            1. Validates user permissions
            2. Processes configuration changes
            3. Updates forwarding settings
            
            Args:
                interaction (discord.Interaction): Command interaction
                setting (str, optional): Setting to modify (default: view)
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
                from modules.mod.reaction_forward.config_cmd import reaction_forward_config
                await reaction_forward_config.callback(interaction, setting, value)
            except Exception as e:
                logger.error(f"Error executing reaction-forward-config command: {str(e)}")
                await interaction.response.send_message(
                    "An error occurred while executing the command.",
                    ephemeral=True
                )
            
            logger.debug(f"Reaction-forward-config command executed by {interaction.user}")
        
        registered_commands.append("reaction-forward-config")
        registered_count += 1
    except Exception as e:
        logger.error(f"Error registering reaction-forward-config command: {e}")
    
    try:
        # Register link-reaction-config command
        @bot.tree.command(
            name="link-reaction-config",
            description="Configure the link reaction feature and manage store settings"
        )
        @app_commands.describe(
            action="The action to perform (view, enable, disable, categories, blacklist, stores)",
            store_id="The store ID to configure (for stores action)",
            setting="The setting to modify for the selected store or feature",
            value="The new value for the setting"
        )
        @app_commands.choices(
            action=[
                app_commands.Choice(name="View Configuration", value="view"),
                app_commands.Choice(name="Enable Feature", value="enable"),
                app_commands.Choice(name="Disable Feature", value="disable"),
                app_commands.Choice(name="Manage Categories", value="categories"),
                app_commands.Choice(name="Manage Blacklist", value="blacklist"),
                app_commands.Choice(name="Manage Stores", value="stores")
            ]
        )
        async def link_reaction_config(
            interaction: discord.Interaction, 
            action: str = "view",
            store_id: str = None,
            setting: str = None,
            value: str = None
        ):
            """
            Configure link reaction and store settings.
            
            This command:
            1. Validates user permissions
            2. Processes configuration changes
            3. Updates store settings
            
            Args:
                interaction (discord.Interaction): Command interaction
                action (str, optional): Action to perform (default: view)
                store_id (str, optional): Store ID to configure
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
                from modules.mod.link_reaction.config_cmd import link_reaction_config
                await link_reaction_config.callback(interaction, action, store_id, setting, value)
            except Exception as e:
                logger.error(f"Error executing link-reaction-config command: {str(e)}")
                await interaction.response.send_message(
                    "An error occurred while executing the command.",
                    ephemeral=True
                )
            
            logger.debug(f"Link-reaction-config command executed by {interaction.user}")
        
        registered_commands.append("link-reaction-config")
        registered_count += 1
    except Exception as e:
        logger.error(f"Error registering link-reaction-config command: {e}")
    
    try:
        # Register mod-config command
        @bot.tree.command(
            name="mod-config",
            description="Configure module-wide settings"
        )
        @app_commands.describe(
            setting="The setting to configure (whitelist)",
            action="The action to perform (add, remove, clear, view)",
            value="The value for the action (role ID or mention)"
        )
        @app_commands.choices(
            setting=[
                app_commands.Choice(name="Whitelist Roles", value="whitelist")
            ],
            action=[
                app_commands.Choice(name="View Current Settings", value="view"),
                app_commands.Choice(name="Add Role", value="add"),
                app_commands.Choice(name="Remove Role", value="remove"),
                app_commands.Choice(name="Clear All Roles", value="clear")
            ]
        )
        async def mod_config(
            interaction: discord.Interaction, 
            setting: str = "whitelist", 
            action: str = "view", 
            value: str = None
        ):
            """
            Configure module-wide settings.
            
            This command:
            1. Validates user permissions
            2. Processes configuration changes
            3. Updates module settings
            
            Args:
                interaction (discord.Interaction): Command interaction
                setting (str, optional): Setting to configure (default: whitelist)
                action (str, optional): Action to perform (default: view)
                value (str, optional): Value for the action
                
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
                from modules.mod.config_cmd import mod_config
                await mod_config.callback(interaction, setting, action, value)
            except Exception as e:
                logger.error(f"Error executing mod-config command: {str(e)}")
                await interaction.response.send_message(
                    "An error occurred while executing the command.",
                    ephemeral=True
                )
            
            logger.debug(f"Mod-config command executed by {interaction.user}")
        
        registered_commands.append("mod-config")
        registered_count += 1
    except Exception as e:
        logger.error(f"Error registering mod-config command: {e}")
    
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