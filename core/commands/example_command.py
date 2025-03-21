"""
path: core/commands/example_command.py
purpose: Example command implementation using BaseCommand
critical:
- Demonstrates proper command implementation
- Shows permission handling
- Includes error handling
"""

from .base import BaseCommand
import discord

class PingCommand(BaseCommand):
    """Example ping command implementation."""
    
    def __init__(self):
        super().__init__(
            name="ping",
            description="Check bot latency",
            permissions=None,  # No permissions required
            guild_only=False  # Can be used in DMs
        )
    
    async def execute(self, interaction: discord.Interaction) -> None:
        """
        Execute the ping command.
        
        Args:
            interaction: The Discord interaction
        """
        latency = round(interaction.client.latency * 1000)
        await interaction.response.send_message(
            f"🏓 Pong! Bot latency: {latency}ms",
            ephemeral=True
        ) 