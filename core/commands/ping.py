"""
path: core/commands/ping.py
purpose: Implements the ping command to check bot latency
critical:
- Provides latency information
- Uses base command class
- Implements standard error handling
"""

import time
import discord
from .base import BaseCommand
from ..command_registry import registry

class PingCommand(BaseCommand):
    """Command to check bot latency."""
    
    def __init__(self):
        """Initialize the ping command."""
        super().__init__(
            name="ping",
            description="Check if the bot is responsive and view latency"
        )
        
    async def execute(self, interaction: discord.Interaction, **kwargs) -> None:
        """
        Execute the ping command.
        
        Args:
            interaction: The Discord interaction
            **kwargs: Additional arguments (unused)
        """
        try:
            # Calculate latency
            start_time = time.time()
            await interaction.response.defer(ephemeral=False)
            end_time = time.time()
            
            latency = round((end_time - start_time) * 1000)
            
            # Send response
            await interaction.followup.send(f"Pong! 🏓 Latency: {latency}ms")
            
        except Exception as e:
            await self.handle_error(interaction, e)

# Register the command
registry.register_command(PingCommand()) 