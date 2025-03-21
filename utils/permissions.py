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
from core.permissions import permission_manager, Permission

logger = logging.getLogger('discord_bot.utils.permissions')

# Define module-specific permissions
MODULE_PERMISSIONS = {
    'mod': 'mod.*',
    'online': 'online.*',
    'instore': 'instore.*',
    'redeye': 'redeye.*'
}

def get_whitelisted_roles(module_name: str) -> List[int]:
    """
    Get the list of whitelisted role IDs for a specific module.
    This function is maintained for backward compatibility.
    New code should use the permission system directly.
    
    Args:
        module_name: The name of the module (mod, online, instore)
        
    Returns:
        List of role IDs as integers
    """
    env_var = f"{module_name.upper()}_WHITELIST_ROLE_IDS"
    role_ids_str = os.getenv(env_var, '')
    
    try:
        # Parse comma-separated role IDs into integers
        role_ids = [int(role_id.strip()) for role_id in role_ids_str.split(',') if role_id.strip()]
        
        # Register these roles with the permission system
        permission_name = MODULE_PERMISSIONS.get(module_name.lower())
        if permission_name:
            for role_id in role_ids:
                try:
                    permission_manager.assign_role_permission(role_id, permission_name)
                except Exception as e:
                    logger.warning(f"Failed to assign permission {permission_name} to role {role_id}: {e}")
        
        return role_ids
    except ValueError as e:
        logger.error(f"Error parsing role IDs for module {module_name}: {e}")
        return []

def has_module_permission(user: Union[Member, User], module_name: str) -> bool:
    """
    Check if a user has permission to use a specific module.
    Uses the new permission system while maintaining backward compatibility.
    
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
        
    # If we have a discord.User instead of a Member, we can't check roles
    if not isinstance(user, Member):
        logger.debug(f"User {user} is not a Member, can't check roles")
        return False
        
    # Check permission using the new system
    permission_name = MODULE_PERMISSIONS.get(module_name.lower())
    if permission_name:
        has_permission = permission_manager.has_permission(user, permission_name)
        logger.debug(f"Permission check for {user} on {module_name}: {has_permission}")
        return has_permission
        
    # Fallback to old system if module not registered in new system
    whitelisted_roles = get_whitelisted_roles(module_name)
    if not whitelisted_roles:
        logger.debug(f"No whitelist defined for module {module_name}, denying access")
        return False
        
    user_role_ids = {role.id for role in user.roles}
    has_permission = any(role_id in user_role_ids for role_id in whitelisted_roles)
    
    if has_permission:
        logger.debug(f"User {user} has permission for module {module_name} (legacy check)")
    else:
        logger.debug(f"User {user} does not have permission for module {module_name} (legacy check)")
        
    return has_permission

async def check_interaction_permissions(interaction: Interaction, module_name: str) -> bool:
    """
    Check if the user who triggered an interaction has permission for a module.
    
    Args:
        interaction: The Discord interaction to check
        module_name: The name of the module (mod, online, instore)
        
    Returns:
        True if the user has permission
        
    Raises:
        app_commands.CheckFailure: If the user doesn't have permission
    """
    if has_module_permission(interaction.user, module_name):
        return True
        
    user_name = interaction.user.display_name
    module_display_name = module_name.capitalize()
    raise app_commands.CheckFailure(
        f"User {user_name} doesn't have permission to use {module_display_name} module commands"
    )

def mod_only():
    """
    Decorator to check if a user has permission to use mod commands.
    
    Returns:
        A decorator function that checks permissions
    """
    async def predicate(interaction: Interaction):
        return await check_interaction_permissions(interaction, 'mod')
        
    return app_commands.check(predicate)

def redeye_only():
    """
    Decorator to check if a user has permission to use redeye commands.
    
    Returns:
        A decorator function that checks permissions
    """
    async def predicate(interaction: Interaction):
        return await check_interaction_permissions(interaction, 'redeye')
        
    return app_commands.check(predicate)

def require_permissions(module_name: str):
    """
    Decorator to check if a user has permission to use commands from a specific module.
    
    Args:
        module_name: The name of the module (mod, online, instore, redeye)
        
    Returns:
        A decorator function that checks permissions
    """
    async def predicate(interaction: Interaction):
        return await check_interaction_permissions(interaction, module_name)
        
    return app_commands.check(predicate)

# Register module-specific permissions
for module_name, permission_name in MODULE_PERMISSIONS.items():
    try:
        permission_manager.register_permission(
            Permission(permission_name, f"Full access to {module_name} module")
        )
    except Exception as e:
        logger.warning(f"Failed to register permission for module {module_name}: {e}")

# Initialize permissions from environment
for module_name in MODULE_PERMISSIONS:
    get_whitelisted_roles(module_name) 