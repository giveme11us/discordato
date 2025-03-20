"""
Online Help Command

Provides help information for the online module.
"""

import discord
from discord import app_commands
import logging
from utils.permissions import require_permissions
from config.features.embed_config import embed as embed_config

logger = logging.getLogger('discord_bot.modules.online.help_cmd')

async def handle_online_help(interaction):
    """
    Handle the online help command.
    
    Args:
        interaction: The Discord interaction
    """
    embed = discord.Embed(
        title="Online Module Help",
        description="The Online module provides functionality for online product monitoring and management."
    )
    
    # Apply styling from embed_config
    embed = embed_config.apply_default_styling(embed)
    
    # Add placeholder information
    embed.add_field(
        name="🛍️ Online Monitoring",
        value="This module is currently in development. Features will be added in future updates.",
        inline=False
    )
    
    # Add placeholder for future commands
    embed.add_field(
        name="Upcoming Features",
        value="• Product monitoring\n• Stock notifications\n• Price tracking\n• Availability alerts",
        inline=False
    )
    
    # Add note about development
    embed.add_field(
        name="Development Status",
        value="This module is actively being developed. Stay tuned for updates!",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

def setup_help_cmd(bot):
    """
    Set up the online_help command.
    
    Args:
        bot: The Discord bot to add the command to
    """
    logger.info("Setting up online_help command")
    
    @bot.tree.command(
        name="online_help",
        description="Display help information for the online module"
    )
    @require_permissions('online')
    async def online_help(interaction: discord.Interaction):
        """
        Display help information for the online module.
        
        Args:
            interaction: The Discord interaction
        """
        await handle_online_help(interaction)
    
    logger.info("Successfully set up online_help command") 