"""
Ping Command

A simple ping command to check if the bot is responsive.
"""

import logging
import time
import discord
from discord import app_commands

logger = logging.getLogger('discord_bot.modules.mod.ping')

async def ping_command(interaction: discord.Interaction):
    """
    Ping command handler.
    
    Args:
        interaction: The Discord interaction
    """
    # Calculate latency
    start_time = time.time()
    await interaction.response.defer(ephemeral=False)
    end_time = time.time()
    
    latency = round((end_time - start_time) * 1000)
    
    # Send response
    await interaction.followup.send(f"Pong! 🏓 Latency: {latency}ms")
    
    logger.debug(f"Ping command executed by {interaction.user} with latency {latency}ms")

def setup_ping(bot):
    """
    Register the ping command with the bot.
    
    Args:
        bot: The Discord bot instance
    """
    @bot.tree.command(
        name="ping",
        description="Check if the bot is responsive and view latency"
    )
    async def ping(interaction: discord.Interaction):
        await ping_command(interaction)
    
    logger.debug("Registered ping command") 