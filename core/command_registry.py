"""
path: core/command_registry.py
purpose: Provides a central registry for all commands in the bot
critical:
- Ensures commands are properly registered and synced
- Prevents duplicate command registration
- Maintains command metadata
"""

import logging
import discord
from discord import app_commands
from typing import Dict, Set, Optional
from .commands.base import BaseCommand

logger = logging.getLogger('discord_bot.command_registry')

class CommandRegistry:
    """Central registry for all bot commands."""
    
    def __init__(self):
        """Initialize the command registry."""
        self._commands: Dict[str, BaseCommand] = {}
        self._registered_commands: Set[str] = set()
        
    def register_command(self, command: BaseCommand) -> None:
        """
        Register a new command.
        
        Args:
            command: The command to register
            
        Raises:
            ValueError: If command with same name already exists
        """
        if command.name in self._commands:
            raise ValueError(f"Command '{command.name}' is already registered")
            
        self._commands[command.name] = command
        logger.info(f"Registered command: {command.name}")
        
    def get_command(self, name: str) -> Optional[BaseCommand]:
        """
        Get a registered command by name.
        
        Args:
            name: The name of the command
            
        Returns:
            The command if found, None otherwise
        """
        return self._commands.get(name)
        
    def register_with_bot(self, bot: discord.Client) -> None:
        """
        Register all commands with the Discord bot.
        
        Args:
            bot: The Discord bot instance
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
        """Get the set of registered command names."""
        return self._registered_commands.copy()
        
    def __len__(self) -> int:
        """Get the number of registered commands."""
        return len(self._commands)
        
    def __iter__(self):
        """Iterate over registered commands."""
        return iter(self._commands.values())

# Global registry instance
registry = CommandRegistry()

def register_all_commands(bot: discord.Client) -> None:
    """
    Register all commands with the bot.
    This ensures that commands are properly registered before syncing.
    
    Args:
        bot: The Discord bot instance
    """
    logger.info("Registering all commands centrally")
    
    try:
        # Register commands with Discord
        registry.register_with_bot(bot)
        logger.info(f"Successfully registered {len(registry)} commands")
    except Exception as e:
        logger.error(f"Error registering commands: {e}")

def register_all_commands(bot):
    """
    Register all commands with the bot.
    This ensures that commands are properly registered before syncing.
    
    Args:
        bot: The Discord bot instance
    """
    logger.info("Registering all commands centrally")
    registered_count = 0
    
    # Track registered commands for logging
    registered_commands = []
    
    try:
        # Register ping command
        @bot.tree.command(
            name="ping",
            description="Check if the bot is responsive and view latency"
        )
        async def ping(interaction: discord.Interaction):
            # Calculate latency
            import time
            start_time = time.time()
            await interaction.response.defer(ephemeral=False)
            end_time = time.time()
            
            latency = round((end_time - start_time) * 1000)
            
            # Send response
            await interaction.followup.send(f"Pong! 🏓 Latency: {latency}ms")
            
            logger.debug(f"Ping command executed by {interaction.user} with latency {latency}ms")
        
        registered_commands.append("ping")
        registered_count += 1
    except Exception as e:
        logger.error(f"Error registering ping command: {e}")
    
    try:
        # Register hi command
        @bot.tree.command(
            name="hi",
            description="Get a friendly greeting from the bot"
        )
        async def hi(interaction: discord.Interaction):
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
    except Exception as e:
        logger.error(f"Error registering hi command: {e}")
    
    # Register number command
    @bot.tree.command(
        name="number",
        description="Generate a random number within a specified range"
    )
    @app_commands.describe(
        min_value="The minimum value (default: 1)",
        max_value="The maximum value (default: 100)"
    )
    async def number(interaction: discord.Interaction, min_value: int = 1, max_value: int = 100):
        import random
        if min_value >= max_value:
            await interaction.response.send_message("Error: Minimum value must be less than maximum value.", ephemeral=True)
            return
        
        number = random.randint(min_value, max_value)
        await interaction.response.send_message(f"🎲 Your random number between {min_value} and {max_value} is: **{number}**")
        logger.debug(f"Number command executed by {interaction.user}")
    
    # Register pinger-config command
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
        # Check if user has administrator permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You need administrator permissions to use this command.", ephemeral=True)
            return
            
        # Delegate to the pinger module
        try:
            from modules.mod.pinger.config_cmd import config_command
            await config_command(interaction, setting, value)
        except Exception as e:
            logger.error(f"Error executing pinger-config command: {str(e)}")
            await interaction.response.send_message("An error occurred while executing the command.", ephemeral=True)
            
        logger.debug(f"Pinger-config command executed by {interaction.user}")
    
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
        # Check if user has administrator permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You need administrator permissions to use this command.", ephemeral=True)
            return
            
        # Delegate to the keyword filter module
        try:
            from modules.mod.keyword_filter.config_cmd import keyword_filter_config
            # Don't call the command object - just let it redirect to our implementation
            # This function is now just a wrapper that will call the original function's implementation
            await keyword_filter_config.callback(interaction, action, filter_id, setting, value)
        except Exception as e:
            logger.error(f"Error executing keyword-filter-config command: {str(e)}")
            await interaction.response.send_message("An error occurred while executing the command.", ephemeral=True)
            
        logger.debug(f"Keyword-filter-config command executed by {interaction.user}")
    
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
        # Check if user has administrator permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You need administrator permissions to use this command.", ephemeral=True)
            return
            
        # Delegate to the keyword filter module
        try:
            from modules.mod.keyword_filter.config_cmd import keyword_filter_quicksetup
            # Access the command's callback function instead of calling the command object directly
            await keyword_filter_quicksetup.callback(interaction, source_channel, notification_channel, keywords)
        except Exception as e:
            logger.error(f"Error executing keyword-filter-quicksetup command: {str(e)}")
            await interaction.response.send_message("An error occurred while executing the command.", ephemeral=True)
            
        logger.debug(f"Keyword-filter-quicksetup command executed by {interaction.user}")
    
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
        # Check if user has administrator permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You need administrator permissions to use this command.", ephemeral=True)
            return
            
        # Delegate to the reaction forward module
        try:
            from modules.mod.reaction_forward.config_cmd import handle_reaction_forward_config
            await handle_reaction_forward_config(interaction, setting, value)
        except Exception as e:
            logger.error(f"Error executing reaction-forward-config command: {str(e)}")
            await interaction.response.send_message("An error occurred while executing the command.", ephemeral=True)
            
        logger.debug(f"Reaction-forward-config command executed by {interaction.user}")
    
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
        # Check if user has administrator permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You need administrator permissions to use this command.", ephemeral=True)
            return
            
        # Delegate to the link reaction module
        try:
            from modules.mod.link_reaction.config_cmd import link_reaction_config
            # Access the command's callback function
            await link_reaction_config.callback(interaction, action, store_id, setting, value)
        except Exception as e:
            logger.error(f"Error executing link-reaction-config command: {str(e)}")
            await interaction.response.send_message("An error occurred while executing the command.", ephemeral=True)
            
        logger.debug(f"Link-reaction-config command executed by {interaction.user}")
    
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
        # Check if user has administrator permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You need administrator permissions to use this command.", ephemeral=True)
            return
            
        # Delegate to the mod config module
        try:
            from modules.mod.mod_config_cmd import handle_mod_config
            await handle_mod_config(interaction, setting, action, value)
        except Exception as e:
            logger.error(f"Error executing mod-config command: {str(e)}")
            await interaction.response.send_message("An error occurred while executing the command.", ephemeral=True)
            
        logger.debug(f"Mod-config command executed by {interaction.user}")
    
    # Register purge command
    @bot.tree.command(
        name="purge",
        description="Delete a specified number of messages in the current channel"
    )
    @app_commands.describe(
        count="The number of messages to delete (max 100)"
    )
    async def purge(interaction: discord.Interaction, count: int = 10):
        # Check if user has manage messages permission
        if not interaction.user.guild_permissions.manage_messages and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You need manage messages permission to use this command.", ephemeral=True)
            return
            
        # Delegate to the purge module
        try:
            from modules.mod.general.purge import handle_purge
            await handle_purge(interaction, count)
        except Exception as e:
            logger.error(f"Error executing purge command: {str(e)}")
            await interaction.response.send_message("An error occurred while executing the command.", ephemeral=True)
            
        logger.debug(f"Purge command executed by {interaction.user}")
    
    logger.info(f"Registered {registered_count} commands centrally")
    for cmd in registered_commands:
        logger.info(f"  - Registered command: {cmd}")
    
    return registered_count 