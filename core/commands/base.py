"""
path: core/commands/base.py
purpose: Provides base command class and utilities for command implementation
critical:
- All commands should inherit from BaseCommand
- Permissions must be checked before execution
- Error handling must be implemented
"""

import logging
from typing import List, Optional, Union
import discord
from discord import app_commands
from ..permissions import permission_manager, Permission

logger = logging.getLogger(__name__)

class BaseCommand:
    """
    Base class for all bot commands.
    
    Attributes:
        name (str): Command name
        description (str): Command description
        permissions (List[str]): Required permissions
        guild_only (bool): Whether command is guild-only
        is_enabled (bool): Whether command is enabled
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        permissions: Optional[List[str]] = None,
        guild_only: bool = True  # Changed default to True since most commands need guild context
    ):
        self.name = name
        self.description = description
        self.permissions = permissions or []
        self.guild_only = guild_only
        self.is_enabled = True
        
    async def pre_execute(self, interaction: discord.Interaction) -> bool:
        """
        Runs before command execution to check permissions and requirements.
        
        Args:
            interaction: The Discord interaction
            
        Returns:
            bool: Whether the command can proceed
        """
        if not self.is_enabled:
            await interaction.response.send_message(
                "This command is currently disabled.",
                ephemeral=True
            )
            return False
            
        if self.guild_only and not interaction.guild:
            await interaction.response.send_message(
                "This command can only be used in a server.",
                ephemeral=True
            )
            return False
            
        if not await self.check_permissions(interaction):
            return False
            
        return True
        
    async def execute(self, interaction: discord.Interaction) -> None:
        """
        Executes the command logic. Must be implemented by subclasses.
        
        Args:
            interaction: The Discord interaction
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Command must implement execute method")
        
    async def check_permissions(self, interaction: discord.Interaction) -> bool:
        """
        Checks if the user has required permissions using the permission manager.
        
        Args:
            interaction: The Discord interaction
            
        Returns:
            bool: Whether user has required permissions
        """
        if not self.permissions:
            return True
            
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
            
        # Check each required permission
        missing_permissions = []
        for permission in self.permissions:
            if not permission_manager.has_permission(interaction.user, permission):
                missing_permissions.append(permission)
                
        if missing_permissions:
            await interaction.response.send_message(
                f"You're missing the following permissions: {', '.join(missing_permissions)}",
                ephemeral=True
            )
            return False
            
        return True
        
    def register(self, tree: app_commands.CommandTree) -> None:
        """
        Registers the command with the Discord command tree.
        
        Args:
            tree: The Discord command tree
        """
        @tree.command(name=self.name, description=self.description)
        async def command_wrapper(interaction: discord.Interaction):
            try:
                if await self.pre_execute(interaction):
                    await self.execute(interaction)
            except Exception as e:
                logger.error(f"Error executing command {self.name}: {e}", exc_info=True)
                await interaction.response.send_message(
                    "An error occurred while executing this command.",
                    ephemeral=True
                )
                
        logger.info(f"Registered command: {self.name}") 