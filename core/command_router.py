"""
path: core/command_router.py
purpose: Manages command registration and routing
critical:
- Prevents duplicate command registration
- Handles command routing and execution
- Manages command groups and categories
"""

import logging
from typing import Dict, Optional, Type, List
import discord
from discord import app_commands
from .commands.base import BaseCommand
from .error_handler import handle_interaction_error, CommandError

logger = logging.getLogger(__name__)

class CommandRouter:
    """
    Manages command registration and routing.
    
    Attributes:
        bot (discord.Client): The Discord bot instance
        commands (Dict[str, BaseCommand]): Registered commands
        command_groups (Dict[str, app_commands.Group]): Command groups
    """
    
    def __init__(self, bot: discord.Client):
        """
        Initialize the command router.
        
        Args:
            bot: The Discord bot instance
        """
        self.bot = bot
        self.commands: Dict[str, BaseCommand] = {}
        self.command_groups: Dict[str, app_commands.Group] = {}
        
    def register_command(self, command: BaseCommand) -> None:
        """
        Register a new command.
        
        Args:
            command: The command to register
            
        Raises:
            CommandError: If command already exists
        """
        if command.name in self.commands:
            raise CommandError(f"Command '{command.name}' is already registered")
            
        self.commands[command.name] = command
        command.register(self.bot.tree)
        logger.info(f"Registered command: {command.name}")
        
    def register_group(
        self,
        name: str,
        description: str,
        commands: Optional[List[BaseCommand]] = None
    ) -> app_commands.Group:
        """
        Create and register a command group.
        
        Args:
            name: Group name
            description: Group description
            commands: List of commands to add to group
            
        Returns:
            app_commands.Group: The created command group
            
        Raises:
            CommandError: If group already exists
        """
        if name in self.command_groups:
            raise CommandError(f"Command group '{name}' already exists")
            
        group = app_commands.Group(name=name, description=description)
        self.command_groups[name] = group
        
        if commands:
            for command in commands:
                if command.name in self.commands:
                    raise CommandError(f"Command '{command.name}' is already registered")
                self.commands[command.name] = command
                
        self.bot.tree.add_command(group)
        logger.info(f"Registered command group: {name}")
        return group
        
    def unregister_command(self, name: str) -> None:
        """
        Unregister a command.
        
        Args:
            name: Name of command to unregister
        """
        if name in self.commands:
            del self.commands[name]
            # Note: Discord.py doesn't provide a way to remove commands at runtime
            # They will be removed on next sync
            logger.info(f"Unregistered command: {name}")
            
    def unregister_group(self, name: str) -> None:
        """
        Unregister a command group.
        
        Args:
            name: Name of group to unregister
        """
        if name in self.command_groups:
            group = self.command_groups[name]
            self.bot.tree.remove_command(group.name, type=group)
            del self.command_groups[name]
            logger.info(f"Unregistered command group: {name}")
            
    async def sync_commands(self) -> None:
        """Sync all commands with Discord."""
        try:
            await self.bot.tree.sync()
            logger.info("Successfully synced commands with Discord")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}", exc_info=e)
            raise CommandError("Failed to sync commands with Discord")
            
    def get_command(self, name: str) -> Optional[BaseCommand]:
        """
        Get a registered command by name.
        
        Args:
            name: Command name
            
        Returns:
            Optional[BaseCommand]: The command if found, None otherwise
        """
        return self.commands.get(name)
        
    def get_group(self, name: str) -> Optional[app_commands.Group]:
        """
        Get a command group by name.
        
        Args:
            name: Group name
            
        Returns:
            Optional[app_commands.Group]: The group if found, None otherwise
        """
        return self.command_groups.get(name) 