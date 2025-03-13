"""
Bot Manager

This module handles bot initialization, lifecycle management,
and operational scenario determination.
"""

import logging
import discord
from discord.ext import commands

from config.environment import get_token, is_development
from config import settings
from core.module_loader import ModuleLoader
from core.command_sync import CommandSync
from core.command_router import CommandRouter
from core.command_registry import register_all_commands

logger = logging.getLogger('discord_bot.bot_manager')

class BotManager:
    """
    Manages the lifecycle and configuration of Discord bot instances.
    Handles different operational scenarios based on token configuration.
    """
    
    def __init__(self):
        """
        Initialize the bot manager.
        Determines the operational scenario and sets up bot instances.
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
        
        Returns:
            str: 'single', 'multi', or 'partial'
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
        Initialize bot instances based on the operational scenario.
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
            register_all_commands(bot)
            
            # Register all modules with this bot
            for module_name in self.modules:
                self.module_loader.load_module(bot, module_name)
            
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
                    
                    # Register only this module with its bot
                    self.module_loader.load_module(bot, module_name)
                    
                    self.bots[module_name] = bot
                    logger.info(f"Initialized bot for module {module_name}")
                else:
                    logger.warning(f"Module {module_name} disabled: no token available")
    
    def start(self):
        """
        Start all bot instances.
        """
        if not self.bots:
            logger.error("No bots to start")
            return
        
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
    
    def stop(self):
        """
        Stop all bot instances.
        """
        for bot_name, bot in self.bots.items():
            logger.info(f"Stopping bot: {bot_name}")
            # Close the bot
            bot.close() 