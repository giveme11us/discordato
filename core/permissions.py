"""
path: core/permissions.py
purpose: Implements role-based access control and permission management
critical:
- Permissions are hierarchical and support wildcards
- Role-based access control is the primary permission mechanism
- Permissions are cached for performance
"""

import logging
import os
from typing import Dict, Set, List, Optional, Union
from dataclasses import dataclass
import discord
from discord import Member, Role, Permissions as DiscordPermissions

logger = logging.getLogger(__name__)

@dataclass
class Permission:
    """
    Represents a permission in the system.
    
    Attributes:
        name: The permission identifier (e.g., "admin.user.create")
        description: Human-readable description of the permission
    """
    name: str
    description: str
    
    def __post_init__(self):
        if not self.name:
            raise PermissionError("Permission name cannot be empty")
        if not self.description:
            raise PermissionError("Permission description required")
        if "*" in self.name and not self.name.endswith(".*"):
            raise PermissionError("Wildcards can only be used at the end of permission names")

class PermissionError(Exception):
    """Custom exception for permission-related errors."""
    pass

class PermissionManager:
    """
    Manages the permission system including role-based access control.
    
    Attributes:
        permissions: Registered permissions
        role_permissions: Mapping of role IDs to their granted permissions
        role_denials: Mapping of role IDs to their explicitly denied permissions
        permission_cache: Cache of permission checks for performance
    """
    
    def __init__(self):
        self.permissions: Dict[str, Permission] = {}
        self.role_permissions: Dict[int, Set[str]] = {}
        self.role_denials: Dict[int, Set[str]] = {}
        self.permission_cache: Dict[str, bool] = {}
        
    def register_permission(self, permission: Permission) -> None:
        """
        Register a new permission in the system.
        
        Args:
            permission: The permission to register
            
        Raises:
            PermissionError: If permission is already registered
        """
        if permission.name in self.permissions:
            raise PermissionError(f"Permission {permission.name} already registered")
        
        self.permissions[permission.name] = permission
        logger.debug(f"Registered permission: {permission.name}")
        
    def register_permissions(self, permissions: List[Permission]) -> None:
        """
        Register multiple permissions at once.
        
        Args:
            permissions: List of permissions to register
        """
        for permission in permissions:
            self.register_permission(permission)
            
    def assign_role_permission(self, role_id: int, permission_name: str) -> None:
        """
        Grant a permission to a role.
        
        Args:
            role_id: The Discord role ID
            permission_name: The name of the permission to grant
            
        Raises:
            PermissionError: If permission doesn't exist
        """
        if permission_name not in self.permissions:
            raise PermissionError(f"Permission {permission_name} not registered")
            
        if role_id not in self.role_permissions:
            self.role_permissions[role_id] = set()
            
        self.role_permissions[role_id].add(permission_name)
        self._clear_cache()
        logger.debug(f"Granted permission {permission_name} to role {role_id}")
        
    def deny_role_permission(self, role_id: int, permission_name: str) -> None:
        """
        Explicitly deny a permission to a role.
        
        Args:
            role_id: The Discord role ID
            permission_name: The name of the permission to deny
        """
        if role_id not in self.role_denials:
            self.role_denials[role_id] = set()
            
        self.role_denials[role_id].add(permission_name)
        self._clear_cache()
        logger.debug(f"Denied permission {permission_name} to role {role_id}")
        
    def revoke_role_permission(self, role_id: int, permission_name: str) -> None:
        """
        Remove a permission from a role.
        
        Args:
            role_id: The Discord role ID
            permission_name: The permission to revoke
        """
        if role_id in self.role_permissions:
            self.role_permissions[role_id].discard(permission_name)
            self._clear_cache()
            logger.debug(f"Revoked permission {permission_name} from role {role_id}")
            
    def has_permission(self, member: Member, permission_name: str) -> bool:
        """
        Check if a member has a specific permission.
        
        Args:
            member: The Discord member
            permission_name: The permission to check
            
        Returns:
            bool: Whether the member has the permission
        """
        # Check cache first
        cache_key = f"{member.id}:{permission_name}"
        if cache_key in self.permission_cache:
            return self.permission_cache[cache_key]
            
        # Server administrators always have all permissions
        if member.guild_permissions.administrator:
            self.permission_cache[cache_key] = True
            return True
            
        # Check for explicit denials first (they take precedence)
        for role in member.roles:
            if role.id in self.role_denials:
                denied_perms = self.role_denials[role.id]
                if self._matches_permission(permission_name, denied_perms):
                    self.permission_cache[cache_key] = False
                    return False
                    
        # Then check for granted permissions
        for role in member.roles:
            if role.id in self.role_permissions:
                granted_perms = self.role_permissions[role.id]
                if self._matches_permission(permission_name, granted_perms):
                    self.permission_cache[cache_key] = True
                    return True
                    
        # No matching permissions found
        self.permission_cache[cache_key] = False
        return False
        
    def _matches_permission(self, permission: str, permission_set: Set[str]) -> bool:
        """
        Check if a permission matches any in a set, including wildcards.
        
        Args:
            permission: The permission to check
            permission_set: Set of permissions to check against
            
        Returns:
            bool: Whether there's a match
        """
        if permission in permission_set:
            return True
            
        # Check for wildcard matches
        permission_parts = permission.split('.')
        for i in range(len(permission_parts)):
            wildcard = '.'.join(permission_parts[:i]) + '.*'
            if wildcard in permission_set:
                return True
                
        return False
        
    def _clear_cache(self) -> None:
        """Clear the permission cache."""
        self.permission_cache.clear()
        logger.debug("Cleared permission cache")

# Initialize the global permission manager
permission_manager = PermissionManager()

def require_permission(permission_name: str):
    """
    Decorator to require a specific permission for a command.
    
    Args:
        permission_name: The required permission
        
    Returns:
        A decorator function that checks for the permission
    """
    async def predicate(interaction: discord.Interaction) -> bool:
        if not isinstance(interaction.user, Member):
            await interaction.response.send_message(
                "This command can only be used in a server.",
                ephemeral=True
            )
            return False
            
        if not permission_manager.has_permission(interaction.user, permission_name):
            await interaction.response.send_message(
                f"You don't have the required permission: {permission_name}",
                ephemeral=True
            )
            return False
            
        return True
        
    return discord.app_commands.check(predicate)

# Register core permissions
core_permissions = [
    Permission("admin.*", "Full administrative access"),
    Permission("admin.user.*", "User management permissions"),
    Permission("admin.user.create", "Create new users"),
    Permission("admin.user.delete", "Delete users"),
    Permission("admin.role.*", "Role management permissions"),
    Permission("admin.role.create", "Create new roles"),
    Permission("admin.role.delete", "Delete roles"),
    Permission("mod.*", "Full moderator access"),
    Permission("mod.message.*", "Message moderation permissions"),
    Permission("mod.message.delete", "Delete messages"),
    Permission("mod.message.pin", "Pin messages"),
    Permission("mod.user.*", "User moderation permissions"),
    Permission("mod.user.kick", "Kick users"),
    Permission("mod.user.ban", "Ban users"),
    Permission("mod.user.timeout", "Timeout users"),
]

# Register core permissions
for permission in core_permissions:
    try:
        permission_manager.register_permission(permission)
    except PermissionError as e:
        logger.warning(f"Failed to register core permission: {e}") 