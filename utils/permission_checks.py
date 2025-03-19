"""
Permission Checks

This module provides utility functions for checking permissions in Discord commands.
"""

import discord
import functools
import logging
from config import admin_roles_config

logger = logging.getLogger('discord_bot.utils.permission_checks')

def is_admin():
    """
    A check that ensures the command can only be used by administrators or users with admin roles.
    
    Returns:
        A check function that can be used as a decorator
    """
    async def predicate(interaction: discord.Interaction):
        # Check if the user has permission
        has_permission = admin_roles_config.has_permission(interaction.user)
        
        if not has_permission:
            logger.warning(f"User {interaction.user} tried to use an admin command without permission")
            await interaction.response.send_message(
                "⛔ You don't have permission to use this command. "
                "You need to be a server administrator or have an admin role.", 
                ephemeral=True
            )
        
        return has_permission
    
    return discord.app_commands.check(predicate)

def command_with_admin_check(name, description, **kwargs):
    """
    A decorator that creates a slash command with an admin permission check.
    
    Args:
        name: The name of the command
        description: The description of the command
        **kwargs: Additional keyword arguments to pass to the command decorator
        
    Returns:
        A decorator that creates a slash command with an admin check
    """
    def decorator(func):
        @is_admin()
        @discord.app_commands.command(name=name, description=description, **kwargs)
        @functools.wraps(func)
        async def wrapper(interaction: discord.Interaction, *args, **kwargs):
            return await func(interaction, *args, **kwargs)
        
        return wrapper
    
    return decorator

def admin_check(interaction: discord.Interaction) -> bool:
    """
    A function to check if a user has admin permissions.
    This can be used inline in command logic.
    
    Args:
        interaction: The Discord interaction
        
    Returns:
        bool: True if the user has permission, False otherwise
    """
    return admin_roles_config.has_permission(interaction.user) 