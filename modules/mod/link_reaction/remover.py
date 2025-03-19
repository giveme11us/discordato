"""
LuisaViaRoma PID Remover Functionality

This module provides functionality for removing PIDs from the LuisaViaRoma tracking file.
"""

import os
import logging
import discord
from config import link_reaction_config

logger = logging.getLogger('discord_bot.modules.mod.link_reaction.remover')

async def remove_pid_from_file(pid, channel=None):
    """
    Remove a PID from the configured LuisaViaRoma file
    
    Args:
        pid: The product ID to remove
        channel: Optional Discord channel to send result messages to
    
    Returns:
        bool: True if the PID was removed, False otherwise
        str: Message describing the result
    """
    # Get LuisaViaRoma store configuration
    stores = link_reaction_config.settings_manager.get("STORES", {})
    
    # Check if we're using the new dictionary format or legacy list format
    store_config = None
    
    if isinstance(stores, dict):
        # Dictionary format (new)
        store_config = stores.get("luisaviaroma", {})
    elif isinstance(stores, list):
        # List format (legacy)
        for store in stores:
            if isinstance(store, dict) and store.get('name', '').lower() == "luisaviaroma":
                store_config = store
                break
    
    if not store_config:
        message = "❌ LuisaViaRoma store not configured."
        logger.error(message)
        if channel:
            await channel.send(message)
        return False, message
    
    # Get file path from store configuration
    file_path = store_config.get('file_path')
    
    if not file_path:
        message = "❌ LuisaViaRoma file path not configured."
        logger.error(message)
        if channel:
            await channel.send(message)
        return False, message
    
    # Check if file exists
    if not os.path.exists(file_path):
        message = f"❌ File not found: {file_path}"
        logger.error(message)
        if channel:
            await channel.send(message)
        return False, message
    
    # Read file content
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
    except Exception as e:
        message = f"❌ Error reading file: {str(e)}"
        logger.error(message)
        if channel:
            await channel.send(message)
        return False, message
    
    # Look for PID in the file
    pid = pid.strip()
    pid_found = False
    new_lines = []
    
    for line in lines:
        line_stripped = line.strip()
        if line_stripped == pid:
            pid_found = True
            # Skip this line (don't add to new_lines)
        elif line_stripped:  # Only add non-empty lines
            new_lines.append(line)
    
    # If PID not found, return early
    if not pid_found:
        message = f"ℹ️ Product ID `{pid}` not found in the LuisaViaRoma tracking list."
        logger.info(message)
        if channel:
            await channel.send(message)
        return False, message
    
    # Write modified content back to file
    try:
        with open(file_path, "w") as f:
            # Make sure each line ends with a newline character
            for i, line in enumerate(new_lines):
                if not line.endswith('\n'):
                    f.write(f"{line}\n")
                else:
                    f.write(line)
        
        message = f"✅ Removed product ID `{pid}` from LuisaViaRoma tracking list."
        logger.info(message)
        if channel:
            await channel.send(message)
        return True, message
    except Exception as e:
        message = f"❌ Error writing to file: {str(e)}"
        logger.error(message)
        if channel:
            await channel.send(message)
        return False, message

def setup_remover_commands(bot):
    """Register user context menu command for removing PIDs"""
    logger.info("Setting up LuisaViaRoma remover user commands")
    
    # Import required libraries
    import discord.app_commands as app_commands
    from discord import app_commands
    from typing import Optional
    from utils.permissions import check_permissions
    
    # Create a "Remove PID" context menu command that works on users
    @bot.tree.context_menu(name="Remove PID")
    async def remove_pid_context_menu(interaction: discord.Interaction, user: discord.User):
        # Check if the user has permission to use this command
        if not await check_permissions(interaction.user, 'mod'):
            await interaction.response.send_message("⚠️ You don't have permission to use this command.", ephemeral=True)
            return
        
        # Get the most recent message from the user that contains a PID
        channel = interaction.channel
        async for message in channel.history(limit=50):
            if message.author == user:
                # Check for PIDs in message content
                potential_pid = message.content.strip()
                
                # If the message is likely a PID (no spaces, not too long)
                if ' ' not in potential_pid and len(potential_pid) < 100:
                    success, result_message = await remove_pid_from_file(potential_pid, channel)
                    await interaction.response.send_message(
                        f"{result_message}\nTarget User: {user.mention}\nPID: `{potential_pid}`", 
                        ephemeral=True
                    )
                    return
        
        # If no valid PID found
        await interaction.response.send_message(
            f"❌ No valid PID found in recent messages from {user.mention}.", 
            ephemeral=True
        )
    
    logger.info("Successfully set up LuisaViaRoma remover user commands") 