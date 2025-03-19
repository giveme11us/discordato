"""
General Commands Cog

This cog provides general utility commands for the Discord bot.
"""

import discord
from discord.ext import commands
import logging

logger = logging.getLogger('discord_bot.cogs.general_cog')

class GeneralCog(commands.Cog):
    """
    Cog for general utility commands.
    """
    
    def __init__(self, bot):
        """
        Initialize the general commands cog.
        
        Args:
            bot: The Discord bot instance
        """
        self.bot = bot
        logger.info("Initializing General Commands Cog")
    
    @commands.Cog.listener()
    async def on_ready(self):
        """
        Called when the cog is ready.
        """
        logger.info("General Commands Cog is ready")
    
    @discord.app_commands.command(name="ping", description="Check if the bot is responsive and view latency")
    async def ping(self, interaction: discord.Interaction):
        """
        Simple ping command to check bot latency.
        """
        # Calculate latency
        import time
        start_time = time.time()
        await interaction.response.defer(ephemeral=False)
        end_time = time.time()
        
        latency = round((end_time - start_time) * 1000)
        
        # Send response
        await interaction.followup.send(f"Pong! 🏓 Latency: {latency}ms")
        
        logger.debug(f"Ping command executed by {interaction.user} with latency {latency}ms")
    
    @discord.app_commands.command(
        name="purge",
        description="Delete a specified number of messages from the channel"
    )
    @discord.app_commands.describe(
        limit="The number of messages to delete (1-100)"
    )
    async def purge(self, interaction: discord.Interaction, limit: int = 10):
        """
        Delete a specified number of messages from the channel.
        
        Args:
            interaction: The interaction object
            limit: The number of messages to delete (default: 10)
        """
        # Validate the limit
        if limit < 1:
            await interaction.response.send_message("You must delete at least 1 message.", ephemeral=True)
            return
        
        if limit > 100:
            await interaction.response.send_message("You cannot delete more than 100 messages at once.", ephemeral=True)
            return
        
        # Defer the response to buy time for message deletion
        await interaction.response.defer(ephemeral=True)
        
        # Get the channel
        channel = interaction.channel
        
        try:
            # Delete the messages
            deleted = await channel.purge(limit=limit)
            
            # Send a confirmation message
            await interaction.followup.send(f"Deleted {len(deleted)} messages.", ephemeral=True)
            
            # Log the action
            logger.info(f"{interaction.user} purged {len(deleted)} messages in #{channel.name}")
        except discord.Forbidden:
            await interaction.followup.send("I don't have permission to delete messages in this channel.", ephemeral=True)
            logger.warning(f"Bot lacks permission to delete messages in #{channel.name}")
        except discord.HTTPException as e:
            await interaction.followup.send(f"An error occurred while deleting messages: {str(e)}", ephemeral=True)
            logger.error(f"HTTP error while purging messages in #{channel.name}: {str(e)}")

async def setup(bot):
    """
    Setup function for the general commands cog.
    
    Args:
        bot: The Discord bot instance
    """
    await bot.add_cog(GeneralCog(bot))
    logger.info("General Commands Cog added to bot") 