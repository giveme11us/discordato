"""
Purge Command

This module provides a slash command to delete a specified number 
of messages in a channel. Only users with whitelisted roles can use this command.
"""

import logging
import discord
from discord import app_commands
from discord.ext import commands
from config.features.moderation import mod

logger = logging.getLogger('discord_bot.modules.mod.general.purge')

async def handle_purge(interaction, count):
    """
    Handle the purge command - delete a specified number of messages.
    
    Args:
        interaction: The Discord interaction
        count: The number of messages to delete
    """
    # Check if user has a whitelisted role
    if mod.WHITELIST_ROLE_IDS:
        # Convert user's roles to set of IDs for quick lookup
        user_role_ids = {role.id for role in interaction.user.roles}
        
        # Check if any of the user's roles is in the whitelist
        has_whitelisted_role = any(role_id in user_role_ids for role_id in mod.WHITELIST_ROLE_IDS)
        
        if not has_whitelisted_role:
            await interaction.response.send_message(
                "You don't have permission to use this command. You need a whitelisted role.",
                ephemeral=True
            )
            logger.warning(f"User {interaction.user} attempted to use the purge command without having a whitelisted role")
            return
    
    # Verify count is valid
    try:
        count_int = int(count)
        if count_int <= 0:
            await interaction.response.send_message(
                "Please provide a positive number of messages to delete.",
                ephemeral=True
            )
            return
        elif count_int > 100:
            await interaction.response.send_message(
                "You can only delete up to 100 messages at a time for safety reasons.",
                ephemeral=True
            )
            return
    except ValueError:
        await interaction.response.send_message(
            "Please provide a valid number of messages to delete.",
            ephemeral=True
        )
        return
    
    # Defer the response since this might take a moment
    await interaction.response.defer(ephemeral=True)
    
    try:
        # Delete the messages
        deleted = await interaction.channel.purge(limit=count_int)
        
        # Notify the user
        await interaction.followup.send(
            f"Successfully deleted {len(deleted)} messages.",
            ephemeral=True
        )
        
        logger.info(f"User {interaction.user} purged {len(deleted)} messages in channel {interaction.channel.name}")
    except discord.Forbidden:
        await interaction.followup.send(
            "I don't have permission to delete messages in this channel.",
            ephemeral=True
        )
        logger.error(f"Bot lacks permission to delete messages in channel {interaction.channel.name}")
    except discord.HTTPException as e:
        await interaction.followup.send(
            f"An error occurred while deleting messages: {str(e)}",
            ephemeral=True
        )
        logger.error(f"HTTP error while purging messages: {str(e)}")

def setup_purge(bot):
    """
    Register the purge slash command.
    
    Args:
        bot: The Discord bot instance
    """
    logger.info("Registering purge command")
    
    @bot.tree.command(
        name="purge",
        description="Delete a specified number of messages in the current channel"
    )
    @app_commands.describe(
        count="The number of messages to delete (max 100)"
    )
    async def purge(interaction: discord.Interaction, count: int):
        await handle_purge(interaction, count)
        
    logger.info("Registered purge command") 