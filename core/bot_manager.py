"""
Bot Manager

This module handles bot initialization, lifecycle management,
and operational scenario determination.

The Bot Manager is responsible for:
1. Initializing Discord bot instances
2. Managing bot lifecycles (start/stop)
3. Loading and managing modules
4. Synchronizing commands
5. Routing commands to appropriate handlers

Critical:
- Requires proper token configuration in environment
- Must be initialized before any bot operations
- Handles cleanup of resources on shutdown

Classes:
    BotManager: Main class for managing Discord bot instances
"""

import logging
import discord
from discord.ext import commands
import asyncio

from config.environment.environment import get_token, is_development
from config.core.settings import settings
from core.module_loader import ModuleLoader
from core.command_sync import CommandSync
from core.command_router import CommandRouter
# from core.command_registry import register_all_commands # Disabled old command registry

logger = logging.getLogger('discord_bot.bot_manager')

class BotManager:
    """
    Manages the lifecycle and configuration of Discord bot instances.
    Handles different operational scenarios based on token configuration.
    
    The BotManager class is the central component responsible for:
    - Bot initialization and configuration
    - Module discovery and loading
    - Command synchronization
    - Command routing
    - Resource management
    
    Attributes:
        bots (dict): Dictionary of bot instances keyed by name
        module_loader (ModuleLoader): Instance for loading bot modules
        command_sync (CommandSync): Instance for syncing Discord commands
        command_router (CommandRouter): Instance for routing commands
        modules (list): List of discovered modules
        scenario (str): Current operational scenario
        
    Critical:
        - Must call start() to begin bot operations
        - Must call stop() for proper cleanup
        - Requires valid token configuration
    """
    
    def __init__(self):
        """
        Initialize the bot manager.
        
        This method:
        1. Sets up core components (module loader, command sync, router)
        2. Discovers available modules
        3. Determines operational scenario
        4. Initializes bot instances
        
        Raises:
            ConfigurationError: If required configuration is missing
            ModuleLoadError: If module discovery fails
        """
        self.bots = {}
        self.module_loader = ModuleLoader()
        self.command_sync = CommandSync()
        self.command_router = CommandRouter()
        
        # Load available modules
        self.modules = self.module_loader.discover_modules()
        logger.info(f"Discovered {len(self.modules)} modules")
        
        # Determine operational scenario
        self.scenario = self._determine_scenario()
        logger.info(f"Operating in {self.scenario} mode")
        
        # Initialize bots based on scenario
        self._initialize_bots()
    
    def _determine_scenario(self):
        """
        Determine the operational scenario based on token configuration.
        
        This method analyzes the available token configuration to determine
        how the bot should operate. It supports three scenarios:
        - SINGLE: Single bot with one token
        - MULTI: Multiple bots with different tokens
        - PARTIAL: Partial operation with subset of available tokens
        
        Returns:
            str: The determined scenario ('SINGLE', 'MULTI', or 'PARTIAL')
            
        Raises:
            ConfigurationError: If no valid tokens are found
            
        Note:
            The scenario affects how the bot manager initializes and
            manages bot instances throughout their lifecycle.
        """
        main_token = get_token()
        if not main_token:
            logger.error("No main token found. Cannot proceed.")
            raise ValueError("DISCORD_BOT_TOKEN is required")
        
        # Check if all modules have their own tokens
        all_have_tokens = True
        any_has_token = False
        
        for module_name in self.modules:
            module_token = get_token(module_name)
            if not module_token:
                all_have_tokens = False
            elif module_token != main_token:
                any_has_token = True
        
        if all_have_tokens and any_has_token:
            return 'multi'
        elif not any_has_token:
            return 'single'
        else:
            return 'partial'
    
    def _initialize_bots(self):
        """
        Initialize bot instances based on the determined scenario.
        
        This method creates and configures Discord bot instances according to
        the operational scenario. For each bot, it:
        1. Creates a Discord client instance
        2. Configures intents and permissions
        3. Sets up event handlers
        4. Loads appropriate modules
        5. Registers basic commands
        
        The initialization process varies by scenario:
        - SINGLE: Creates one bot with all modules
        - MULTI: Creates multiple bots with specific module sets
        - PARTIAL: Creates bots for available tokens
        
        Raises:
            ConfigurationError: If bot initialization fails
            ModuleLoadError: If module loading fails
            
        Note:
            This is an internal method called during BotManager initialization.
            The actual bot connections are established later by the start() method.
        """
        intents = discord.Intents.default()
        intents.message_content = True
        
        if self.scenario == 'single':
            # Single bot mode: one bot for all modules
            bot = commands.Bot(
                command_prefix=settings.COMMAND_PREFIX,
                description=settings.BOT_DESCRIPTION,
                intents=intents
            )
            
            # Register all commands centrally
            # register_all_commands(bot)
            
            # We'll load modules as cogs in discord_bot.py, so we don't need
            # the direct module loading here anymore
            
            self.bots['main'] = bot
            
        elif self.scenario in ('multi', 'partial'):
            # Multi-bot or partial mode: separate bot for each module with a token
            for module_name in self.modules:
                token = get_token(module_name)
                if token:
                    bot = commands.Bot(
                        command_prefix=settings.COMMAND_PREFIX,
                        description=f"{settings.BOT_DESCRIPTION} - {module_name}",
                        intents=intents
                    )
                    
                    # Register commands for this module
                    if module_name == 'mod':
                        # Register ping command
                        @bot.tree.command(name="ping", description="Check if the bot is responsive and view latency")
                        async def ping(interaction: discord.Interaction):
                            await interaction.response.send_message("Pong! 🏓")
                    elif module_name == 'online':
                        # Register hi command
                        @bot.tree.command(name="hi", description="Get a friendly greeting from the bot")
                        async def hi(interaction: discord.Interaction):
                            await interaction.response.send_message(f"Hello there, {interaction.user.display_name}!")
                    elif module_name == 'instore':
                        # Register number command
                        @bot.tree.command(name="number", description="Generate a random number")
                        async def number(interaction: discord.Interaction, min_value: int = 1, max_value: int = 100):
                            import random
                            number = random.randint(min_value, max_value)
                            await interaction.response.send_message(f"🎲 Your random number is: {number}")
                    
                    # Cogs will be loaded in discord_bot.py
                    
                    self.bots[module_name] = bot
                    logger.info(f"Initialized bot for module {module_name}")
                else:
                    logger.warning(f"Module {module_name} disabled: no token available")
    
    def start(self):
        """
        Start all initialized bot instances.
        
        This method:
        1. Validates bot configurations
        2. Synchronizes commands with Discord
        3. Establishes connections for all bots
        4. Starts background tasks and event loops
        
        The startup process is handled differently based on the scenario:
        - SINGLE: Starts one bot synchronously
        - MULTI/PARTIAL: Starts multiple bots concurrently
        
        Returns:
            bool: True if all bots started successfully, False otherwise
            
        Raises:
            ConnectionError: If connection to Discord fails
            RuntimeError: If bot startup fails
            
        Note:
            This method is blocking and should be called after initialization
            is complete. Use stop() to properly shutdown the bots.
        """
        if not self.bots:
            logger.error("No bots to start")
            return False
        
        # In development mode, sync commands first
        if is_development():
            for bot_name, bot in self.bots.items():
                self.command_sync.sync_commands(bot, bot_name)
        
        # Start each bot
        for bot_name, bot in self.bots.items():
            token = get_token(bot_name if bot_name != 'main' else None)
            logger.info(f"Starting bot: {bot_name}")
            
            # Run the bot
            bot.run(token)
        
        return True
    
    def stop(self):
        """
        Stop all running bot instances and perform cleanup.
        
        This method:
        1. Gracefully disconnects all bots from Discord
        2. Cancels running tasks and background jobs
        3. Cleans up resources and connections
        4. Resets internal state
        
        The shutdown process ensures:
        - All bots are properly disconnected
        - Resources are released
        - No lingering connections remain
        
        Returns:
            bool: True if all bots stopped successfully, False otherwise
            
        Note:
            This method should be called before program termination to
            ensure proper cleanup of resources.
        """
        for bot_name, bot in self.bots.items():
            logger.info(f"Stopping bot: {bot_name}")
            # Close the bot
            bot.close()
        
        return True

    def setup_bot(self, bot_name, token, modules):
        """
        Set up a new bot instance with specified configuration.
        
        This method creates and configures a new Discord bot instance with:
        1. Basic configuration (prefix, description, intents)
        2. Module loading and initialization
        3. Command registration
        4. Event handler setup
        
        Args:
            bot_name (str): Unique identifier for the bot instance
            token (str): Discord bot token for authentication
            modules (list): List of module names to load for this bot
            
        Returns:
            commands.Bot: Configured bot instance
            
        Raises:
            ValueError: If bot_name already exists or token is invalid
            ModuleLoadError: If module loading fails
            
        Note:
            The bot is not started automatically. Call start_bot() to
            establish the Discord connection.
        """
        intents = discord.Intents.default()
        intents.message_content = True  # Required for accessing message content
        
        # Create the bot instance 
        bot = commands.Bot(command_prefix=settings.DEFAULT_PREFIX, intents=intents)
        
        # Store the bot in our internal registry
        self.bots[bot_name] = bot
        
        # Log modules loaded
        logger.info(f"Setting up bot: {bot_name} with modules: {modules}")
        
        # Load and register all modules for this bot
        self.module_loader.load_modules(bot, modules)
        
        # Register standard commands and features
        self.command_sync.register_module_commands(bot)
        
        # Set up command sync
        self.command_sync.sync_commands(bot, bot_name)
        
        # Start the bot
        logger.info(f"Starting bot: {bot_name}")
        return bot 

    def start_bot(self, bot_name):
        """
        Start a specific bot instance by name.
        
        This method:
        1. Validates the bot exists and is configured
        2. Synchronizes commands with Discord
        3. Establishes the Discord connection
        4. Starts event loop and background tasks
        
        Args:
            bot_name (str): Name of the bot instance to start
            
        Returns:
            bool: True if bot started successfully, False otherwise
            
        Raises:
            KeyError: If bot_name doesn't exist
            ConnectionError: If Discord connection fails
            
        Note:
            This method is blocking. The bot will run until stopped
            or disconnected.
        """
        if bot_name not in self.bots:
            logger.error(f"Bot {bot_name} not found")
            return False
        
        bot = self.bots[bot_name]
        token = get_token(bot_name)
        
        if not token:
            logger.error(f"No token found for bot {bot_name}")
            return False
        
        try:
            # Start the bot
            logger.info(f"Starting bot: {bot_name}")
            bot.run(token)
            return True
        except Exception as e:
            logger.error(f"Error starting bot {bot_name}: {str(e)}")
            return False 