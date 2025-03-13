"""
Hi Command

A greeting command that responds with a personalized message.
"""

import logging
import random
import discord
from discord import app_commands

logger = logging.getLogger('discord_bot.modules.online.hi')

# List of greetings
GREETINGS = [
    "Hello there, {}! How are you doing today?",
    "Hi, {}! Nice to see you!",
    "Hey {}! What's up?",
    "Greetings, {}! How can I assist you today?",
    "Hi there {}! Hope you're having a great day!"
]

async def hi_command(interaction: discord.Interaction):
    """
    Hi command handler.
    
    Args:
        interaction: The Discord interaction
    """
    # Get a random greeting
    greeting = random.choice(GREETINGS).format(interaction.user.display_name)
    
    # Send response
    await interaction.response.send_message(greeting)
    
    logger.debug(f"Hi command executed by {interaction.user}")

def setup_hi(bot):
    """
    Register the hi command with the bot.
    
    Args:
        bot: The Discord bot instance
    """
    @bot.tree.command(
        name="hi",
        description="Get a friendly greeting from the bot"
    )
    async def hi(interaction: discord.Interaction):
        await hi_command(interaction)
    
    logger.debug("Registered hi command") 