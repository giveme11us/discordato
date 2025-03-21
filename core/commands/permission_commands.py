"""
path: core/commands/permission_commands.py
purpose: Provides commands for managing permissions and roles
critical:
- Only administrators can manage permissions
- Changes are validated before being applied
- All operations are logged
"""

import logging
from typing import Optional
import discord
from discord import app_commands
from ..permissions import permission_manager, Permission
from .base import BaseCommand

logger = logging.getLogger(__name__)

class ListPermissionsCommand(BaseCommand):
    """Command to list all available permissions."""
    
    def __init__(self):
        super().__init__(
            name="permissions",
            description="List all available permissions",
            permissions=["admin.role.*"]
        )
        
    async def execute(self, interaction: discord.Interaction) -> None:
        # Group permissions by category
        categories = {}
        for perm in permission_manager.permissions.values():
            category = perm.name.split('.')[0]
            if category not in categories:
                categories[category] = []
            categories[category].append(perm)
            
        # Create embed
        embed = discord.Embed(
            title="Available Permissions",
            color=discord.Color.blue()
        )
        
        for category, perms in categories.items():
            # Sort permissions by name
            perms.sort(key=lambda p: p.name)
            # Create field content
            content = "\n".join(f"`{p.name}` - {p.description}" for p in perms)
            embed.add_field(
                name=f"{category.capitalize()} Permissions",
                value=content,
                inline=False
            )
            
        await interaction.response.send_message(embed=embed, ephemeral=True)

class AssignPermissionCommand(BaseCommand):
    """Command to assign a permission to a role."""
    
    def __init__(self):
        super().__init__(
            name="assign_permission",
            description="Assign a permission to a role",
            permissions=["admin.role.*"]
        )
        
    @app_commands.describe(
        role="The role to assign the permission to",
        permission="The permission to assign"
    )
    async def execute(self, interaction: discord.Interaction, role: discord.Role, permission: str) -> None:
        try:
            # Verify permission exists
            if permission not in permission_manager.permissions:
                await interaction.response.send_message(
                    f"Permission '{permission}' does not exist.",
                    ephemeral=True
                )
                return
                
            # Assign permission
            permission_manager.assign_role_permission(role.id, permission)
            
            await interaction.response.send_message(
                f"Assigned permission '{permission}' to role {role.mention}",
                ephemeral=True
            )
            logger.info(f"User {interaction.user} assigned permission {permission} to role {role.name} ({role.id})")
            
        except Exception as e:
            logger.error(f"Error assigning permission: {e}", exc_info=True)
            await interaction.response.send_message(
                f"Error assigning permission: {str(e)}",
                ephemeral=True
            )

class RevokePermissionCommand(BaseCommand):
    """Command to revoke a permission from a role."""
    
    def __init__(self):
        super().__init__(
            name="revoke_permission",
            description="Revoke a permission from a role",
            permissions=["admin.role.*"]
        )
        
    @app_commands.describe(
        role="The role to revoke the permission from",
        permission="The permission to revoke"
    )
    async def execute(self, interaction: discord.Interaction, role: discord.Role, permission: str) -> None:
        try:
            # Verify permission exists
            if permission not in permission_manager.permissions:
                await interaction.response.send_message(
                    f"Permission '{permission}' does not exist.",
                    ephemeral=True
                )
                return
                
            # Revoke permission
            permission_manager.revoke_role_permission(role.id, permission)
            
            await interaction.response.send_message(
                f"Revoked permission '{permission}' from role {role.mention}",
                ephemeral=True
            )
            logger.info(f"User {interaction.user} revoked permission {permission} from role {role.name} ({role.id})")
            
        except Exception as e:
            logger.error(f"Error revoking permission: {e}", exc_info=True)
            await interaction.response.send_message(
                f"Error revoking permission: {str(e)}",
                ephemeral=True
            )

class ListRolePermissionsCommand(BaseCommand):
    """Command to list all permissions assigned to a role."""
    
    def __init__(self):
        super().__init__(
            name="role_permissions",
            description="List all permissions assigned to a role",
            permissions=["admin.role.*"]
        )
        
    @app_commands.describe(
        role="The role to list permissions for"
    )
    async def execute(self, interaction: discord.Interaction, role: discord.Role) -> None:
        # Get permissions for role
        role_perms = permission_manager.role_permissions.get(role.id, set())
        role_denials = permission_manager.role_denials.get(role.id, set())
        
        # Create embed
        embed = discord.Embed(
            title=f"Permissions for {role.name}",
            color=role.color
        )
        
        if role_perms:
            # Sort permissions
            sorted_perms = sorted(role_perms)
            perms_text = "\n".join(f"`{p}`" for p in sorted_perms)
            embed.add_field(
                name="Granted Permissions",
                value=perms_text,
                inline=False
            )
        else:
            embed.add_field(
                name="Granted Permissions",
                value="No permissions granted",
                inline=False
            )
            
        if role_denials:
            # Sort denied permissions
            sorted_denials = sorted(role_denials)
            denials_text = "\n".join(f"`{p}`" for p in sorted_denials)
            embed.add_field(
                name="Denied Permissions",
                value=denials_text,
                inline=False
            )
            
        await interaction.response.send_message(embed=embed, ephemeral=True)

class DenyPermissionCommand(BaseCommand):
    """Command to explicitly deny a permission to a role."""
    
    def __init__(self):
        super().__init__(
            name="deny_permission",
            description="Explicitly deny a permission to a role",
            permissions=["admin.role.*"]
        )
        
    @app_commands.describe(
        role="The role to deny the permission to",
        permission="The permission to deny"
    )
    async def execute(self, interaction: discord.Interaction, role: discord.Role, permission: str) -> None:
        try:
            # Verify permission exists
            if permission not in permission_manager.permissions:
                await interaction.response.send_message(
                    f"Permission '{permission}' does not exist.",
                    ephemeral=True
                )
                return
                
            # Deny permission
            permission_manager.deny_role_permission(role.id, permission)
            
            await interaction.response.send_message(
                f"Denied permission '{permission}' to role {role.mention}",
                ephemeral=True
            )
            logger.info(f"User {interaction.user} denied permission {permission} to role {role.name} ({role.id})")
            
        except Exception as e:
            logger.error(f"Error denying permission: {e}", exc_info=True)
            await interaction.response.send_message(
                f"Error denying permission: {str(e)}",
                ephemeral=True
            )

# List of all permission management commands
permission_commands = [
    ListPermissionsCommand(),
    AssignPermissionCommand(),
    RevokePermissionCommand(),
    ListRolePermissionsCommand(),
    DenyPermissionCommand()
] 