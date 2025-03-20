"""
In-store Help Command

Provides help information for the in-store module.
"""

import discord
from discord import app_commands
import logging
from utils.permissions import require_permissions
from config.features.embed_config import embed as embed_config

logger = logging.getLogger('discord_bot.modules.instore.help_cmd')

async def handle_instore_help(interaction):
    """
    Handle the in-store help command.
    
    Args:
        interaction: The Discord interaction
    """
    embed = discord.Embed(
        title="In-store Module Help",
        description="The In-store module provides functionality for tracking in-store product availability and events."
    )
    
    # Apply styling from embed_config
    embed = embed_config.apply_default_styling(embed)
    
    # Add placeholder information
    embed.add_field(
        name="🏬 In-store Monitoring",
        value="This module is currently in development. Features will be added in future updates.",
        inline=False
    )
    
    # Add placeholder for future commands
    embed.add_field(
        name="Upcoming Features",
        value="• Store location tracking\n• Release event notifications\n• In-store restock alerts\n• Regional availability reports",
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
    Set up the instore_help command.
    
    Args:
        bot: The Discord bot to add the command to
    """
    logger.info("Setting up instore_help command")
    
    @bot.tree.command(
        name="instore_help",
        description="Display help information for the in-store module"
    )
    @require_permissions('instore')
    async def instore_help(interaction: discord.Interaction):
        """
        Display help information for the in-store module.
        
        Args:
            interaction: The Discord interaction
        """
        await handle_instore_help(interaction)
    
    logger.info("Successfully set up instore_help command") 