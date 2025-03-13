"""
Command Registry

This module provides a central registry for all commands in the bot.
It ensures that commands are properly registered and synced.
"""

import logging
import discord
from discord import app_commands

logger = logging.getLogger('discord_bot.command_registry')

def register_all_commands(bot):
    """
    Register all commands with the bot.
    This ensures that commands are properly registered before syncing.
    
    Args:
        bot: The Discord bot instance
    """
    logger.info("Registering all commands centrally")
    
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
    
    logger.info(f"Registered {len(bot.tree.get_commands())} commands centrally") 