"""
Redeye Help Command

Provides help information for the redeye module.
"""

import discord
from discord import app_commands
import logging
from utils.permissions import redeye_only
from config.features.embed_config import embed as embed_config

logger = logging.getLogger('discord_bot.modules.redeye.help_cmd')

async def handle_redeye_help(interaction):
    """
    Handle the redeye help command.
    
    Args:
        interaction: The Discord interaction
    """
    embed = discord.Embed(
        title="Redeye Module Help",
        description="The Redeye module provides functionality for viewing and managing profiles stored in CSV files."
    )
    
    # Apply styling from embed_config
    embed = embed_config.apply_default_styling(embed)
    
    # Add general information
    embed.add_field(
        name="👤 Profile Management",
        value="View and manage profiles stored in CSV files.\n`/redeye-profiles` - View profiles\n`/redeye-config` - Configure file paths",
        inline=False
    )
    
    # Add detailed command information
    embed.add_field(
        name="/redeye-profiles",
        value="View all profiles or details for a specific profile.\n**Parameters:**\n`profile_name` - (Optional) Name of a specific profile to view",
        inline=False
    )
    
    embed.add_field(
        name="/redeye-config",
        value="View or update file path configurations.\n**Parameters:**\n`profiles_path` - (Optional) Path to profiles CSV file\n`tasks_path` - (Optional) Path to tasks CSV file",
        inline=False
    )
    
    # Add examples
    examples = (
        "**Examples:**\n"
        "`/redeye-profiles` - Show all profiles\n"
        "`/redeye-profiles profile_name:MyProfile1` - Show details for a specific profile\n"
        "`/redeye-config` - Show current file paths\n"
        "`/redeye-config profiles_path:/path/to/profiles.csv` - Update profiles file path"
    )
    embed.add_field(name="Command Examples", value=examples, inline=False)
    
    # Add CSV file format information
    file_format = (
        "**profiles.csv columns:**\n"
        "Name, Webhook, FirstName, LastName, Phone, CountryId, Address, ZipCode, City, StateId, CodFisc\n\n"
        "**tasks.csv columns:**\n"
        "ProfileName, Pid, Email, Password"
    )
    embed.add_field(name="File Format", value=file_format, inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

def setup_help_cmd(bot):
    """
    Set up the redeye_help command.
    
    Args:
        bot: The Discord bot to add the command to
    """
    logger.info("Setting up redeye_help command")
    
    @bot.tree.command(
        name="redeye_help",
        description="Display help information for the redeye module"
    )
    @redeye_only()
    async def redeye_help(interaction: discord.Interaction):
        """
        Display help information for the redeye module.
        
        Args:
            interaction: The Discord interaction
        """
        await handle_redeye_help(interaction)
    
    logger.info("Successfully set up redeye_help command") 