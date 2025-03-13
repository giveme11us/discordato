"""
Number Command

A command that generates a random number within a specified range.
"""

import logging
import random
import discord
from discord import app_commands

logger = logging.getLogger('discord_bot.modules.instore.number')

async def number_command(interaction: discord.Interaction, min_value: int = 1, max_value: int = 100):
    """
    Number command handler.
    
    Args:
        interaction: The Discord interaction
        min_value: The minimum value (inclusive)
        max_value: The maximum value (inclusive)
    """
    # Validate input
    if min_value >= max_value:
        await interaction.response.send_message("Error: Minimum value must be less than maximum value.", ephemeral=True)
        return
    
    # Generate random number
    number = random.randint(min_value, max_value)
    
    # Send response
    await interaction.response.send_message(f"🎲 Your random number between {min_value} and {max_value} is: **{number}**")
    
    logger.debug(f"Number command executed by {interaction.user} with range {min_value}-{max_value}, result: {number}")

def setup_number(bot):
    """
    Register the number command with the bot.
    
    Args:
        bot: The Discord bot instance
    """
    @bot.tree.command(
        name="number",
        description="Generate a random number within a specified range"
    )
    @app_commands.describe(
        min_value="The minimum value (default: 1)",
        max_value="The maximum value (default: 100)"
    )
    async def number(interaction: discord.Interaction, min_value: int = 1, max_value: int = 100):
        await number_command(interaction, min_value, max_value)
    
    logger.debug("Registered number command") 