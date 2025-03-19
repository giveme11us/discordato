"""
Number Command

Placeholder for future in-store number functionality.
"""

import logging
import discord
from discord import app_commands

logger = logging.getLogger('discord_bot.modules.instore.number')

async def handle_number_command(interaction: discord.Interaction):
    """
    Placeholder handler for the number command.
    
    Args:
        interaction: The Discord interaction
    """
    await interaction.response.send_message(
        "This feature is coming soon!",
        ephemeral=True
    )

def setup_number(bot):
    """
    Set up the number command.
    
    Args:
        bot: The Discord bot to add the command to
    """
    @bot.tree.command(
        name="store-number",
        description="In-store number functionality (coming soon)"
    )
    async def number(interaction: discord.Interaction):
        await handle_number_command(interaction)
    
    logger.debug("Registered number command") 