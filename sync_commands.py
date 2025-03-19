#!/usr/bin/env python3
"""
Synchronize slash commands with Discord.

This script connects to Discord and synchronizes 
the defined slash commands with the Discord API.
"""

import os
import discord
import logging
import dotenv
import asyncio
import sys
from discord.ext import commands
from discord import app_commands

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
dotenv.load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GUILD_IDS_STR = os.getenv('GUILD_IDS', '')
logger.info(f"Raw GUILD_IDS: {GUILD_IDS_STR}")

# Parse guild IDs
GUILD_IDS = []
if GUILD_IDS_STR:
    try:
        GUILD_IDS = [int(gid.strip()) for gid in GUILD_IDS_STR.split(',') if gid.strip()]
        logger.info(f"Parsed guild IDs: {GUILD_IDS}")
    except ValueError as e:
        logger.error(f"Error parsing guild IDs: {e}")

# Configure the bot with appropriate intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

# Define our custom exit function to be called after syncing
async def exit_after_sync():
    # Wait a short time to ensure sync is complete
    await asyncio.sleep(5)
    logger.info("Exiting after command sync...")
    await bot.close()
    sys.exit(0)

# Event handlers for the bot
@bot.event
async def on_ready():
    logger.info(f"Bot {bot.user.name} is ready")
    
    # Define all commands
    
    # Basic commands
    @bot.tree.command(name="ping", description="Sends a simple ping message")
    async def ping(interaction: discord.Interaction):
        await interaction.response.send_message("Pong! 🏓")
        logger.info(f"Ping command executed by {interaction.user}")

    @bot.tree.command(name="hi", description="Says hello")
    async def hi(interaction: discord.Interaction):
        await interaction.response.send_message(f"Hello, {interaction.user.mention}!")
        logger.info(f"Hi command executed by {interaction.user}")

    @bot.tree.command(name="number", description="Generate a random number")
    @app_commands.describe(min="Minimum value (default: 1)", max="Maximum value (default: 100)")
    async def number(interaction: discord.Interaction, min: int = 1, max: int = 100):
        import random
        number = random.randint(min, max)
        await interaction.response.send_message(f"Your random number is: {number}")
        logger.info(f"Number command executed by {interaction.user} with range {min}-{max}")
    
    # Pinger config command
    @bot.tree.command(
        name="pinger-config",
        description="Configure the pinger feature"
    )
    @app_commands.describe(
        action="The action to perform (add, remove, list)",
        user="The user to add or remove",
        role="The role to add or remove"
    )
    async def pinger_config(
        interaction: discord.Interaction, 
        action: str = None, 
        user: discord.User = None, 
        role: discord.Role = None
    ):
        # This is just a placeholder that will be overridden by the actual implementation
        await interaction.response.send_message("Pinger configuration command registered")
        logger.info(f"Pinger-config command executed by {interaction.user}")
    
    # Reaction forward config command
    @bot.tree.command(
        name="reaction-forward-config",
        description="Configure the reaction forward feature"
    )
    @app_commands.describe(
        setting="The setting to view or modify (categories, enable, disable, forwarding, blacklist)",
        value="The new value for the setting"
    )
    async def reaction_forward_config(
        interaction: discord.Interaction, 
        setting: str = None, 
        value: str = None
    ):
        # This is just a placeholder that will be overridden by the actual implementation
        await interaction.response.send_message("Reaction forward configuration command registered")
        logger.info(f"Reaction-forward-config command executed by {interaction.user}")
    
    # Link reaction config command
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
    async def link_reaction_config(
        interaction: discord.Interaction, 
        action: str = "view",
        store_id: str = None,
        setting: str = None,
        value: str = None
    ):
        # This is just a placeholder that will be overridden by the actual implementation
        await interaction.response.send_message("Link reaction configuration command registered")
        logger.info(f"Link-reaction-config command executed by {interaction.user}")
    
    # Keyword filter config command
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
        # This is just a placeholder that will be overridden by the actual implementation
        await interaction.response.send_message("Keyword filter configuration command registered")
        logger.info(f"Keyword-filter-config command executed by {interaction.user}")
    
    # Keyword filter quicksetup command
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
        # This is just a placeholder that will be overridden by the actual implementation
        await interaction.response.send_message("Keyword filter quicksetup command registered")
        logger.info(f"Keyword-filter-quicksetup command executed by {interaction.user}")
    
    # Mod config command
    @bot.tree.command(
        name="mod-config",
        description="Configure moderation settings"
    )
    @app_commands.describe(
        setting="The setting to configure (whitelist)",
        action="The action to perform (add, remove, clear, view)",
        value="The value for the action (role ID or mention)"
    )
    async def mod_config(
        interaction: discord.Interaction, 
        setting: str = None, 
        action: str = None, 
        value: str = None
    ):
        # This is just a placeholder that will be overridden by the actual implementation
        await interaction.response.send_message("Mod configuration command registered")
        logger.info(f"Mod-config command executed by {interaction.user}")
    
    # Purge command
    @bot.tree.command(
        name="purge",
        description="Delete a specified number of messages from the channel"
    )
    @app_commands.describe(
        limit="The number of messages to delete (1-100)"
    )
    async def purge(
        interaction: discord.Interaction, 
        limit: int = 10
    ):
        # This is just a placeholder that will be overridden by the actual implementation
        await interaction.response.send_message(f"Purge command registered (limit: {limit})")
        logger.info(f"Purge command executed by {interaction.user}")
    
    # Log the total number of commands registered
    logger.info(f"Registered {len(bot.tree.get_commands())} commands")
    
    # Sync commands with guild(s)
    for guild_id in GUILD_IDS:
        try:
            guild = bot.get_guild(guild_id)
            if guild:
                await bot.tree.sync(guild=guild)
                logger.info(f"Synced {len(bot.tree.get_commands())} commands to guild: {guild.name} ({guild_id})")
            else:
                logger.warning(f"Guild not found: {guild_id}")
        except Exception as e:
            logger.error(f"Error syncing commands to guild {guild_id}: {e}")
    
    # Schedule the exit after sync
    bot.loop.create_task(exit_after_sync())

if __name__ == "__main__":
    try:
        logger.info("Starting bot...")
        bot.run(TOKEN)
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        sys.exit(1) 