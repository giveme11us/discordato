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
    
    logger.info("Registered all commands")

async def main():
    # Load environment variables
    load_dotenv()
    
    # Get Discord token
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        logger.error("No Discord token found. Set DISCORD_BOT_TOKEN in .env file.")
        return
    
    # Get guild IDs
    guild_ids_str = os.getenv('GUILD_IDS', '')
    guild_ids = [int(id) for id in guild_ids_str.split(',') if id]
    
    # Create bot instance with necessary intents
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='/', intents=intents)
    
    # Register all commands
    register_commands(bot)
    
    @bot.event
    async def on_ready():
        logger.info(f"Bot {bot.user.name} is ready")
        
        # Sync to specific guilds
        if guild_ids:
            for guild_id in guild_ids:
                await sync_commands(bot, guild_id)
        else:
            # Sync globally
            await sync_commands(bot)
        
        # Disconnect after syncing
        await bot.close()
    
    try:
        await bot.start(token)
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 