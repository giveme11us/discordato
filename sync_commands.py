#!/usr/bin/env python3
"""
Command Sync Script

This script manually syncs slash commands to Discord.
"""

import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

import discord
from discord.ext import commands
from discord import app_commands

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('command_sync')

async def sync_commands(bot, guild_id=None):
    """
    Sync commands to a specific guild or globally.
    
    Args:
        bot: The Discord bot instance
        guild_id (int, optional): The guild ID to sync to. If None, syncs globally.
    """
    try:
        await bot.wait_until_ready()
        
        if guild_id:
            guild = bot.get_guild(guild_id)
            if not guild:
                logger.warning(f"Guild with ID {guild_id} not found")
                return
            
            # Sync to specific guild
            synced = await bot.tree.sync(guild=guild)
            logger.info(f"Synced {len(synced)} commands to guild {guild.name} ({guild_id})")
            for cmd in synced:
                logger.info(f"  - {cmd.name}: {cmd.description}")
        else:
            # Sync globally
            synced = await bot.tree.sync()
            logger.info(f"Synced {len(synced)} commands globally")
            for cmd in synced:
                logger.info(f"  - {cmd.name}: {cmd.description}")
            
        return synced
    except Exception as e:
        logger.error(f"Error syncing commands: {str(e)}")
        return []

def register_commands(bot):
    """
    Register all commands from our modules.
    """
    # Register ping command
    @bot.tree.command(name="ping", description="Check if the bot is responsive and view latency")
    async def ping(interaction: discord.Interaction):
        await interaction.response.send_message("Pong! 🏓")
        logger.info(f"Ping command executed by {interaction.user}")
    
    # Register hi command
    @bot.tree.command(name="hi", description="Get a friendly greeting from the bot")
    async def hi(interaction: discord.Interaction):
        await interaction.response.send_message(f"Hello there, {interaction.user.display_name}! How are you doing today?")
        logger.info(f"Hi command executed by {interaction.user}")
    
    # Register number command
    @bot.tree.command(name="number", description="Generate a random number within a specified range")
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
        logger.info(f"Number command executed by {interaction.user}")
    
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
        # This is just a placeholder that will be overridden by the actual implementation
        await interaction.response.send_message("Pinger configuration command registered")
        logger.info(f"Pinger-config command executed by {interaction.user}")
    
    # Register reaction-forward-config command
    @bot.tree.command(
        name="reaction-forward-config",
        description="Configure the reaction forward feature"
    )
    @app_commands.describe(
        setting="The setting to view or modify (categories, enable, disable, forwarding)",
        value="The new value for the setting"
    )
    async def reaction_forward_config(interaction: discord.Interaction, setting: str = None, value: str = None):
        # This is just a placeholder that will be overridden by the actual implementation
        await interaction.response.send_message("Reaction forward configuration command registered")
        logger.info(f"Reaction-forward-config command executed by {interaction.user}")
    
    # Register mod-config command
    @bot.tree.command(
        name="mod-config",
        description="Configure module-wide settings"
    )
    @app_commands.describe(
        setting="The setting to view or modify (whitelist)",
        action="The action to perform (add, remove, clear, view)",
        value="The value for the action (role mention or ID)"
    )
    async def mod_config(
        interaction: discord.Interaction, 
        setting: str = None, 
        action: str = None, 
        value: str = None
    ):
        # This is just a placeholder that will be overridden by the actual implementation
        await interaction.response.send_message("Module configuration command registered")
        logger.info(f"Mod-config command executed by {interaction.user}")
    
    # Register purge command
    @bot.tree.command(
        name="purge",
        description="Delete a specified number of messages in the current channel"
    )
    @app_commands.describe(
        count="The number of messages to delete (max 100)"
    )
    async def purge(
        interaction: discord.Interaction, 
        count: int
    ):
        # This is just a placeholder that will be overridden by the actual implementation
        await interaction.response.send_message("Purge command registered")
        logger.info(f"Purge command executed by {interaction.user}")
    
    logger.info("Registered all commands")

async def main():
    # Load environment variables
    load_dotenv()
    
    # Get Discord token
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        logger.error("No Discord token found. Set DISCORD_BOT_TOKEN in .env file.")
        return
    
    # Get guild IDs - handle more robustly
    guild_ids_str = os.getenv('GUILD_IDS', '')
    guild_ids = []
    
    # Log the raw value for debugging
    logger.info(f"Raw GUILD_IDS from .env: '{guild_ids_str}'")
    
    # Handle different potential formats
    if guild_ids_str:
        if ',' in guild_ids_str:
            # Handle comma-separated list
            for id_str in guild_ids_str.split(','):
                if id_str.strip():
                    try:
                        guild_ids.append(int(id_str.strip()))
                    except ValueError:
                        logger.error(f"Invalid guild ID format: {id_str}")
        else:
            # Handle single value
            try:
                if guild_ids_str.strip():
                    guild_ids.append(int(guild_ids_str.strip()))
            except ValueError:
                logger.error(f"Invalid guild ID format: {guild_ids_str}")
    
    logger.info(f"Parsed GUILD_IDS: {guild_ids}")
    
    # Create bot instance with necessary intents
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='/', intents=intents)
    
    # Register all commands
    register_commands(bot)
    
    @bot.event
    async def on_ready():
        logger.info(f"Bot {bot.user.name} is ready")
        
        # Log all registered commands
        cmds = bot.tree.get_commands()
        logger.info(f"Bot has {len(cmds)} commands registered")
        for cmd in cmds:
            logger.info(f"  - Command: {cmd.name}")
        
        # Sync to specific guilds
        if guild_ids:
            for guild_id in guild_ids:
                logger.info(f"Syncing commands to guild ID: {guild_id}")
                await sync_commands(bot, guild_id)
        else:
            # Sync globally
            logger.info("No guild IDs found, syncing globally")
            await sync_commands(bot)
        
        # Disconnect after syncing
        await bot.close()
    
    try:
        await bot.start(token)
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 