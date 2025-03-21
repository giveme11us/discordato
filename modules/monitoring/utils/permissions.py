"""
Monitoring Permissions

This module handles permission checks for monitoring commands.
"""

import os
import logging
import discord
from discord import app_commands

logger = logging.getLogger(__name__)

def get_monitoring_whitelist_roles():
    """Get the list of whitelisted role IDs for monitoring commands."""
    role_ids_str = os.getenv('MONITORING_WHITELIST_ROLE_IDS', '')
    return [int(id.strip()) for id in role_ids_str.split(',') if id.strip()]

def require_monitoring_role():
    """
    Decorator to check if user has a monitoring role.
    """
    async def predicate(interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message(
                "This command can only be used in a server.",
                ephemeral=True
            )
            return False
            
        if not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message(
                "Could not verify user permissions.",
                ephemeral=True
            )
            return False
            
        # Get whitelisted role IDs
        whitelist_role_ids = get_monitoring_whitelist_roles()
        logger.debug(f"Checking roles {[role.id for role in interaction.user.roles]} against whitelist {whitelist_role_ids}")
        
        # Check if user has any of the whitelisted roles
        has_role = any(role.id in whitelist_role_ids for role in interaction.user.roles)
        if not has_role:
            await interaction.response.send_message(
                "You need monitoring permissions to use this command.",
                ephemeral=True
            )
            return False
            
        return True

    return app_commands.check(predicate) 