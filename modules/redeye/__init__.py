"""
path: modules/redeye/__init__.py
purpose: Handles redeye profile and task management
critical:
- Manages redeye profiles
- Handles task configuration
- Provides profile commands
"""

import os
import csv
import logging
from typing import Dict, List, Optional
import discord
from discord.ext import commands

logger = logging.getLogger('discord_bot.redeye')

# Configuration
PROFILES_FILE = 'data/redeye/profiles.csv'
TASKS_FILE = 'data/redeye/tasks.csv'

async def setup(bot, registered_commands=None):
    """
    Set up the redeye module.
    
    Args:
        bot: The Discord bot instance
        registered_commands: Set of already registered commands
        
    Returns:
        Set[str]: Updated set of registered commands
    """
    # Initialize registered_commands if not provided
    if registered_commands is None:
        registered_commands = set()
        
    # Register redeye-profiles command if not already registered
    if 'redeye-profiles' not in registered_commands:
        @bot.tree.command(
            name="redeye-profiles",
            description="View all redeye profiles"
        )
        async def redeye_profiles(interaction: discord.Interaction):
            """View all redeye profiles."""
            try:
                profiles = load_profiles()
                if not profiles:
                    await interaction.response.send_message(
                        "No profiles found.",
                        ephemeral=True
                    )
                    return
                    
                # Create embed for profiles
                embed = discord.Embed(
                    title="Redeye Profiles",
                    color=int(os.getenv('EMBED_COLOR', '00ff1f'), 16)
                )
                
                # Add profiles to embed
                for profile in profiles:
                    # Personal Information
                    personal_info = (
                        f"**Name:** {profile['FirstName']} {profile['LastName']}\n"
                        f"**Phone:** {profile['Phone']}\n"
                        f"**Address:** {profile['Address']}\n"
                        f"**City:** {profile['City']}, {profile['StateId']} {profile['ZipCode']}\n"
                        f"**Country:** {profile['CountryId']}\n"
                        f"**Fiscal Code:** {profile.get('CodFisc', 'N/A')}"
                    )
                    
                    # Timing Settings
                    timing_info = (
                        f"**Timeout:** {profile['TimeoutLowerBound']} - {profile['TimeoutUpperBound']}ms\n"
                        f"**Delay:** {profile['DelayLowerBound']} - {profile['DelayUpperBound']}ms\n"
                        f"**Keep Alive:** {profile['KeepConnectionsAlive']}"
                    )
                    
                    # Connection Settings
                    connection_info = (
                        f"**Webhook:** `{profile['Webhook']}`\n"
                        f"**Proxy URL:** `{profile.get('UpstreamProxyURL', 'N/A')}`\n"
                        f"**Akamai Cookie URL:** `{profile.get('UpstreamAkmaiCookieURL', 'N/A')}`"
                    )
                    
                    # Add fields to embed
                    embed.add_field(
                        name=f"Profile: {profile['Name']}",
                        value="**Personal Information:**\n" + personal_info + "\n\n" +
                              "**Timing Settings:**\n" + timing_info + "\n\n" +
                              "**Connection Settings:**\n" + connection_info,
                        inline=False
                    )
                    
                await interaction.response.send_message(
                    embed=embed,
                    ephemeral=True
                )
                
            except Exception as e:
                logger.error(f"Error displaying profiles: {e}", exc_info=True)
                await interaction.response.send_message(
                    "An error occurred while loading profiles.",
                    ephemeral=True
                )
                
        registered_commands.add('redeye-profiles')
        logger.info("Registered command: redeye-profiles")
        
    return registered_commands

async def teardown(bot):
    """Clean up the redeye module."""
    pass

def load_profiles() -> List[Dict[str, str]]:
    """
    Load profiles from CSV file.
    
    Returns:
        List[Dict[str, str]]: List of profile dictionaries
    """
    profiles = []
    try:
        with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            profiles = list(reader)
    except Exception as e:
        logger.error(f"Error loading profiles: {e}", exc_info=True)
    return profiles

def load_tasks() -> List[Dict[str, str]]:
    """
    Load tasks from CSV file.
    
    Returns:
        List[Dict[str, str]]: List of task dictionaries
    """
    tasks = []
    try:
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            tasks = list(reader)
    except Exception as e:
        logger.error(f"Error loading tasks: {e}", exc_info=True)
    return tasks
