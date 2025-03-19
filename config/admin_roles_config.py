"""
Admin Roles Configuration

This module contains settings for managing admin roles that can use configuration commands.
"""

import json
import os
import logging
from utils.settings_manager import SettingsManager

logger = logging.getLogger('discord_bot.config.admin_roles')

# Default settings
DEFAULT_SETTINGS = {
    # List of role IDs that can use configuration commands
    "ADMIN_ROLE_IDS": [],
    # Whether to allow server administrators to bypass the role check
    "ALLOW_SERVER_ADMINS": True
}

# Initialize settings manager with default settings
settings_manager = SettingsManager(
    settings_file=os.path.join("data", "settings", "admin_roles.json"),
    default_settings=DEFAULT_SETTINGS
)

# Load settings from file or use defaults
settings_manager.load_settings()

def has_permission(member):
    """
    Check if a member has permission to use admin commands.
    
    Args:
        member: The Discord member to check
        
    Returns:
        bool: True if the member has permission, False otherwise
    """
    # Allow server administrators to bypass role check if enabled
    if settings_manager.get("ALLOW_SERVER_ADMINS", True) and member.guild_permissions.administrator:
        return True
    
    # Check if member has any admin role
    admin_role_ids = settings_manager.get("ADMIN_ROLE_IDS", [])
    
    # If no admin roles are configured, only allow server administrators
    if not admin_role_ids:
        return member.guild_permissions.administrator
    
    # Check if member has any of the admin roles
    return any(role.id in admin_role_ids for role in member.roles)

def add_admin_role(role_id):
    """
    Add a role ID to the list of admin roles.
    
    Args:
        role_id: The Discord role ID to add
        
    Returns:
        bool: True if the role was added, False if it was already in the list
    """
    admin_role_ids = settings_manager.get("ADMIN_ROLE_IDS", [])
    
    # Check if role is already in the list
    if role_id in admin_role_ids:
        return False
    
    # Add role to the list
    admin_role_ids.append(role_id)
    settings_manager.set("ADMIN_ROLE_IDS", admin_role_ids)
    
    # Save settings
    return settings_manager.save_settings()

def remove_admin_role(role_id):
    """
    Remove a role ID from the list of admin roles.
    
    Args:
        role_id: The Discord role ID to remove
        
    Returns:
        bool: True if the role was removed, False if it wasn't in the list
    """
    admin_role_ids = settings_manager.get("ADMIN_ROLE_IDS", [])
    
    # Check if role is in the list
    if role_id not in admin_role_ids:
        return False
    
    # Remove role from the list
    admin_role_ids.remove(role_id)
    settings_manager.set("ADMIN_ROLE_IDS", admin_role_ids)
    
    # Save settings
    return settings_manager.save_settings()

def get_admin_roles():
    """
    Get the list of admin role IDs.
    
    Returns:
        list: List of admin role IDs
    """
    return settings_manager.get("ADMIN_ROLE_IDS", [])

def set_allow_server_admins(allow):
    """
    Set whether server administrators can bypass the role check.
    
    Args:
        allow: Whether to allow server administrators
        
    Returns:
        bool: True if the setting was updated successfully
    """
    settings_manager.set("ALLOW_SERVER_ADMINS", allow)
    return settings_manager.save_settings() 