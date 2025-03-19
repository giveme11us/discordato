"""
Permission Utilities

This module provides functions to check if users have the required permissions
for various bot actions based on their roles.
"""

import logging
import os
from typing import Union, List
import discord
from discord import Interaction, Member, User
from discord.ext import commands
from discord import app_commands

logger = logging.getLogger('discord_bot.utils.permissions')

# Define whitelist environment variables for each module
MODULE_WHITELIST_ENV_VARS = {
    'mod': 'MOD_WHITELIST_ROLE_IDS',
    'online': 'ONLINE_WHITELIST_ROLE_IDS',
    'instore': 'INSTORE_WHITELIST_ROLE_IDS',
    'redeye': 'REDEYE_WHITELIST_ROLE_IDS'
}

def get_whitelisted_roles(module_name: str) -> List[int]:
    """
    Get the list of whitelisted role IDs for a specific module.
    
    Args:
        module_name: The name of the module (mod, online, instore)
        
    Returns:
        List of role IDs as integers
    """
    env_var = MODULE_WHITELIST_ENV_VARS.get(module_name.lower())
    if not env_var:
        logger.warning(f"No whitelist environment variable defined for module: {module_name}")
        return []
        
    role_ids_str = os.getenv(env_var, '')
    if not role_ids_str:
        logger.warning(f"No whitelisted roles defined for module: {module_name}")
        return []
        
    try:
        # Parse comma-separated role IDs into integers
        role_ids = [int(role_id.strip()) for role_id in role_ids_str.split(',') if role_id.strip()]
        return role_ids
    except ValueError as e:
        logger.error(f"Error parsing role IDs for module {module_name}: {e}")
        return []

def has_module_permission(user: Union[Member, User], module_name: str) -> bool:
    """
    Check if a user has permission to use a specific module based on their roles.
    
    Args:
        user: The Discord user or member to check
        module_name: The name of the module (mod, online, instore)
        
    Returns:
        True if the user has permission, False otherwise
    """
    # Server owners always have all permissions
    if hasattr(user, 'guild') and user.guild and user.id == user.guild.owner_id:
        logger.debug(f"User {user} is the server owner, granting all permissions")
        return True
        
    # Bot developers can have bypass permissions if needed
    # Uncomment and set your own ID if you want this feature
    # if user.id == YOUR_DISCORD_ID:
    #     return True
    
    # If we have a discord.User instead of a Member, we can't check roles
    if not hasattr(user, 'roles'):
        logger.debug(f"User {user} is not a Member, can't check roles")
        return False
        
    # Get the whitelist for this module
    whitelisted_roles = get_whitelisted_roles(module_name)
    
    # If no whitelist is defined, default to deny access
    if not whitelisted_roles:
        logger.debug(f"No whitelist defined for module {module_name}, denying access")
        return False
        
    # Convert the user's roles to a set of IDs for faster lookup
    user_role_ids = {role.id for role in user.roles}
    
    # Check if the user has any of the whitelisted roles
    has_permission = any(role_id in user_role_ids for role_id in whitelisted_roles)
    
    if has_permission:
        logger.debug(f"User {user} has permission for module {module_name}")
    else:
        logger.debug(f"User {user} does not have permission for module {module_name}")
        
    return has_permission

async def check_interaction_permissions(interaction: Interaction, module_name: str) -> bool:
    """
    Check if the user who triggered an interaction has permission for a module.
    If they don't, raise an app_commands.CheckFailure error.
    
    Args:
        interaction: The Discord interaction to check
        module_name: The name of the module (mod, online, instore)
        
    Returns:
        True if the user has permission, False otherwise
    
    Raises:
        app_commands.CheckFailure: If the user doesn't have permission
    """
    if has_module_permission(interaction.user, module_name):
        return True
        
    # Instead of sending a message directly, raise a specific error
    # that will be caught by the global error handler
    user_name = interaction.user.display_name
    module_display_name = module_name.capitalize()
    raise app_commands.CheckFailure(f"User {user_name} doesn't have permission to use {module_display_name} module commands")

def mod_only():
    """
    Decorator to check if a user has permission to use mod commands.
    Apply this decorator to slash command callbacks to restrict access.
    
    Returns:
        A decorator function that checks permissions
    """
    async def predicate(interaction: Interaction):
        return await check_interaction_permissions(interaction, 'mod')
        
    return app_commands.check(predicate)

def redeye_only():
    """
    Decorator to check if a user has permission to use redeye commands.
    Apply this decorator to slash command callbacks to restrict access to redeye features.
    
    Returns:
        A decorator function that checks permissions specifically for redeye module
    """
    async def predicate(interaction: Interaction):
        return await check_interaction_permissions(interaction, 'redeye')
        
    return app_commands.check(predicate)

def require_permissions(module_name: str):
    """
    Decorator to check if a user has permission to use commands from a specific module.
    Apply this decorator to slash command callbacks to restrict access.
    
    Args:
        module_name: The name of the module (mod, online, instore, redeye)
        
    Returns:
        A decorator function that checks permissions
    """
    async def predicate(interaction: Interaction):
        return await check_interaction_permissions(interaction, module_name)
        
    return app_commands.check(predicate) 