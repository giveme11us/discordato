"""
Link Reaction Commands

Provides commands for configuring link reactions.
"""

import discord
from discord import app_commands
import logging
from utils.permissions import mod_only
from .store_manager import StoreManager
from .adder import add_pid_to_file
from .remover import remove_pid_from_file

logger = logging.getLogger('discord_bot.modules.mod.link_reaction.commands')

def setup_commands(bot):
    """Register link reaction commands."""
    
    @bot.tree.command(
        name="luisaviaroma_adder",
        description="Add a LuisaViaRoma product ID to the tracking list"
    )
    @app_commands.describe(
        pid="The product ID to add"
    )
    @mod_only()
    async def luisaviaroma_adder(interaction: discord.Interaction, pid: str):
        """
        Add a LuisaViaRoma product ID to the tracking list.
        
        Args:
            interaction: The Discord interaction
            pid: The product ID to add
        """
        await interaction.response.defer(ephemeral=True)
        
        # Get store manager
        store_manager = StoreManager()
        store_config = store_manager.get_store("luisaviaroma")
        
        if not store_config:
            await interaction.followup.send("❌ LuisaViaRoma store not configured.", ephemeral=True)
            return
            
        success, message = await add_pid_to_file(pid.strip(), interaction.channel)
        await interaction.followup.send(message, ephemeral=True)
    
    @bot.tree.command(
        name="luisaviaroma_remover",
        description="Remove a LuisaViaRoma product ID from the tracking list"
    )
    @app_commands.describe(
        pid="The product ID to remove"
    )
    @mod_only()
    async def luisaviaroma_remover(interaction: discord.Interaction, pid: str):
        """
        Remove a LuisaViaRoma product ID from the tracking list.
        
        Args:
            interaction: The Discord interaction
            pid: The product ID to remove
        """
        await interaction.response.defer(ephemeral=True)
        
        # Get store manager
        store_manager = StoreManager()
        store_config = store_manager.get_store("luisaviaroma")
        
        if not store_config:
            await interaction.followup.send("❌ LuisaViaRoma store not configured.", ephemeral=True)
            return
            
        success, message = await remove_pid_from_file(pid.strip(), interaction.channel)
        await interaction.followup.send(message, ephemeral=True) 