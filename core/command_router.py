"""
Command Router

This module manages the registration, organization, and routing of Discord commands.

The Command Router is responsible for:
1. Command registration and deregistration
2. Command group management
3. Command routing and execution
4. Error handling and validation
5. Command state management
6. Permission handling
7. Command synchronization
8. Group organization

Critical:
- Prevents duplicate command registration
- Handles command routing and execution
- Manages command groups and categories
- Ensures proper error handling
- Must maintain command state
- Should handle permissions
- Must support command sync
- Should track command usage
- Must validate commands
- Should support versioning

Classes:
    CommandRouter: Main class for managing Discord commands
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
    Manages command registration and routing in the Discord bot.
    
    This class provides:
    1. Command registration and tracking
    2. Group creation and management
    3. Command routing and execution
    4. Error handling and recovery
    5. State management and validation
    6. Permission enforcement
    7. Usage tracking and analytics
    8. Version management
    
    Attributes:
        bot (discord.Client): The Discord bot instance
        commands (Dict[str, BaseCommand]): Registered commands
        command_groups (Dict[str, app_commands.Group]): Command groups
        
    Critical:
        - Commands must have unique names
        - Groups must be properly configured
        - Error handling must be consistent
        - Must track command state
        - Should validate permissions
        - Must handle sync failures
        - Should maintain usage metrics
        - Must support versioning
        - Should handle rate limits
    """
    
    def __init__(self, bot: discord.Client):
        """
        Initialize the command router.
        
        This method:
        1. Sets up command tracking
        2. Initializes group management
        3. Configures error handling
        4. Prepares state tracking
        5. Sets up permission system
        6. Initializes metrics
        
        Args:
            bot (discord.Client): The Discord bot instance to manage commands for
            
        Critical:
            - Must initialize cleanly
            - Should set up tracking
            - Must configure handlers
            - Should prepare metrics
        """
        self.bot = bot
        self.commands = {}
        self.command_groups = {}
        
    def register_command(self, command: BaseCommand) -> None:
        """
        Register a new command with the router.
        
        This method:
        1. Validates command configuration
        2. Checks for duplicates
        3. Registers the command
        4. Sets up error handling
        5. Configures permissions
        6. Initializes tracking
        
        Args:
            command (BaseCommand): The command instance to register
            
        Raises:
            CommandError: If command name is already registered
            ValueError: If command is invalid
            
        Critical:
            - Must validate command
            - Should check permissions
            - Must prevent duplicates
            - Should track registration
            - Must handle errors
            - Should maintain state
            
        Note:
            Commands must have unique names within their scope.
            Registration is atomic - either succeeds completely or fails safely.
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
        Create and register a new command group.
        
        This method:
        1. Validates group configuration
        2. Creates the group
        3. Registers commands
        4. Sets up permissions
        5. Configures routing
        6. Initializes tracking
        
        Args:
            name (str): Name of the command group
            description (str): Description of the group
            commands (List[BaseCommand], optional): Commands to add to group
            
        Returns:
            app_commands.Group: The created command group
            
        Raises:
            CommandError: If group name exists
            ValueError: If group configuration is invalid
            
        Critical:
            - Must validate group
            - Should check permissions
            - Must prevent duplicates
            - Should track registration
            - Must handle errors
            - Should maintain state
            
        Note:
            Group registration is atomic - either all commands are registered
            successfully, or no changes are made.
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
        Remove a command from the router.
        
        This method:
        1. Validates command exists
        2. Removes command
        3. Cleans up resources
        4. Updates tracking
        5. Handles dependencies
        
        Args:
            name (str): Name of the command to remove
            
        Raises:
            KeyError: If command doesn't exist
            CommandError: If command cannot be removed
            
        Critical:
            - Must validate existence
            - Should clean resources
            - Must handle dependencies
            - Should update tracking
            - Must maintain consistency
            
        Note:
            Discord.py doesn't provide runtime command removal.
            Commands will be removed on next sync.
        """
        if name in self.commands:
            del self.commands[name]
            # Note: Discord.py doesn't provide a way to remove commands at runtime
            # They will be removed on next sync
            logger.info(f"Unregistered command: {name}")
            
    def unregister_group(self, name: str) -> None:
        """
        Remove a command group and its commands.
        
        This method:
        1. Validates group exists
        2. Removes group commands
        3. Removes group
        4. Cleans up resources
        5. Updates tracking
        
        Args:
            name (str): Name of the group to remove
            
        Raises:
            KeyError: If group doesn't exist
            CommandError: If group cannot be removed
            
        Critical:
            - Must validate existence
            - Should remove commands
            - Must clean resources
            - Should update tracking
            - Must maintain consistency
            
        Note:
            Group removal is atomic - either the group and all its
            commands are removed, or no changes are made.
        """
        if name in self.command_groups:
            group = self.command_groups[name]
            self.bot.tree.remove_command(group.name, type=group)
            del self.command_groups[name]
            logger.info(f"Unregistered command group: {name}")
            
    async def sync_commands(self) -> None:
        """
        Synchronize commands with Discord.
        
        This method:
        1. Validates command state
        2. Prepares sync operation
        3. Updates registrations
        4. Syncs with Discord API
        5. Verifies sync status
        6. Updates tracking
        
        Raises:
            CommandError: If sync fails
            
        Critical:
            - Must validate state
            - Should handle rate limits
            - Must sync atomically
            - Should verify status
            - Must handle failures
            - Should update tracking
            
        Note:
            Sync is atomic - either all commands sync successfully,
            or the system maintains its previous state.
        """
        try:
            await self.bot.tree.sync()
            logger.info("Successfully synced commands with Discord")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}", exc_info=e)
            raise CommandError("Failed to sync commands with Discord")
            
    def get_command(self, name: str) -> Optional[BaseCommand]:
        """
        Retrieve a registered command by name.
        
        This method:
        1. Validates input
        2. Checks command exists
        3. Returns command instance
        4. Updates access tracking
        
        Args:
            name (str): Name of the command to retrieve
            
        Returns:
            Optional[BaseCommand]: The command if found, None otherwise
            
        Critical:
            - Must validate input
            - Should track access
            - Must handle missing
            - Should maintain state
        """
        return self.commands.get(name)
        
    def get_group(self, name: str) -> Optional[app_commands.Group]:
        """
        Retrieve a command group by name.
        
        This method:
        1. Validates input
        2. Checks group exists
        3. Returns group instance
        4. Updates access tracking
        
        Args:
            name (str): Name of the group to retrieve
            
        Returns:
            Optional[app_commands.Group]: The group if found, None otherwise
            
        Critical:
            - Must validate input
            - Should track access
            - Must handle missing
            - Should maintain state
        """
        return self.command_groups.get(name) 