"""
Error Handler

This module provides centralized error handling for the Discord bot.

The Error Handler is responsible for:
1. Processing and logging errors
2. Providing user-friendly error messages
3. Handling different error types appropriately
4. Maintaining error tracking and statistics
5. Managing error recovery and graceful degradation

Critical:
- Must handle all error types gracefully
- Should provide clear user feedback
- Must maintain proper error logging
- Should track error patterns
- Must ensure error isolation
- Should support error recovery
- Must preserve error context

Classes:
    BotError: Base exception class for bot errors
    CommandError: Command-specific error handling
    ValidationError: Input validation errors
    ConfigurationError: Configuration-related errors
    DatabaseError: Database operation errors
"""

import logging
import traceback
import discord
from discord import app_commands
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class BotError(Exception):
    """
    Base exception class for all bot-related errors.
    
    This class provides:
    1. Structured error information
    2. User-friendly messages
    3. Detailed error context
    4. Error categorization
    
    Attributes:
        message (str): Internal error message for logging
        details (dict): Additional error context and metadata
        user_message (str): User-friendly error message
        
    Critical:
        - Must include clear error messages
        - Should preserve error context
        - Must support user-friendly messages
        - Should maintain error details
    """
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        """
        Initialize the bot error.
        
        This method:
        1. Sets up error message
        2. Stores error details
        3. Configures user message
        4. Initializes base exception
        
        Args:
            message (str): Internal error message
            details (dict, optional): Additional error context
            user_message (str, optional): User-friendly message
            
        Note:
            If user_message is not provided, message is used
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.user_message = user_message or message

class CommandError(BotError):
    """
    Raised when a command fails to execute properly.
    
    This error handles:
    1. Invalid command usage
    2. Command execution failures
    3. Command validation errors
    4. Permission issues
    5. Rate limiting
    
    Critical:
        - Must include command context
        - Should preserve user input
        - Must track command state
        - Should support recovery options
    """
    pass

class ValidationError(BotError):
    """
    Raised when input validation fails.
    
    This error handles:
    1. Invalid parameter values
    2. Missing required fields
    3. Format validation failures
    4. Type mismatches
    5. Range violations
    
    Critical:
        - Must specify invalid fields
        - Should provide correction hints
        - Must preserve input context
        - Should support validation rules
    """
    pass

class ConfigurationError(BotError):
    """
    Raised when configuration issues occur.
    
    This error handles:
    1. Missing configuration
    2. Invalid settings
    3. Environment issues
    4. Dependency problems
    5. Version conflicts
    
    Critical:
        - Must identify config source
        - Should suggest corrections
        - Must track config state
        - Should support fallbacks
    """
    pass

class DatabaseError(BotError):
    """
    Raised when database operations fail.
    
    This error handles:
    1. Connection issues
    2. Query failures
    3. Data integrity errors
    4. Transaction problems
    5. Schema violations
    
    Critical:
        - Must preserve transaction state
        - Should support rollbacks
        - Must track connection state
        - Should handle reconnection
    """
    pass

class ErrorHandler:
    """
    Centralized error handling for the Discord bot.
    
    This class:
    1. Processes and logs errors
    2. Provides user-friendly error messages
    3. Handles different error types appropriately
    4. Maintains error tracking and statistics
    
    Attributes:
        bot (discord.Client): The Discord bot instance
        error_count (int): Number of errors handled
        last_error (Exception): Last error that occurred
    """
    
    def __init__(self, bot: discord.Client):
        """
        Initialize the error handler.
        
        Args:
            bot: The Discord bot instance
        """
        self.bot = bot
        self.error_count = 0
        self.last_error = None
        self.setup_error_handling(bot)
        
    async def handle_interaction_error(self, interaction: discord.Interaction, error: Exception) -> None:
        """
        Handle errors that occur during command interactions.
        
        Args:
            interaction: The Discord interaction
            error: The error that occurred
        """
        try:
            self.error_count += 1
            self.last_error = error
            
            if isinstance(error, app_commands.CommandInvokeError):
                error = error.original
                
            if isinstance(error, BotError):
                await interaction.response.send_message(
                    error.user_message,
                    ephemeral=True
                )
                logger.error(
                    f"Bot error in {interaction.command}",
                    extra={'error': error.message, 'details': error.details}
                )
                
            elif isinstance(error, app_commands.CommandNotFound):
                await interaction.response.send_message(
                    "Command not found. Use /help to see available commands.",
                    ephemeral=True
                )
                logger.warning(
                    f"Unknown command attempted",
                    extra={'command': interaction.command, 'user': str(interaction.user)}
                )
                
            elif isinstance(error, app_commands.MissingPermissions):
                await interaction.response.send_message(
                    "You don't have permission to use this command.",
                    ephemeral=True
                )
                logger.warning(
                    f"Permission denied",
                    extra={
                        'user': str(interaction.user),
                        'command': interaction.command,
                        'missing_permissions': error.missing_permissions
                    }
                )
                
            else:
                await interaction.response.send_message(
                    "An unexpected error occurred. Please try again later.",
                    ephemeral=True
                )
                logger.error(
                    f"Unexpected error",
                    extra={
                        'command': interaction.command,
                        'user': str(interaction.user),
                        'error': str(error)
                    },
                    exc_info=error
                )
                
        except Exception as e:
            logger.critical(
                f"Error handler failure",
                extra={
                    'handler_error': str(e),
                    'original_error': str(error),
                    'command': interaction.command
                },
                exc_info=True
            )
            try:
                await interaction.response.send_message(
                    "An error occurred while processing your command.",
                    ephemeral=True
                )
            except:
                pass
                
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an error with additional context.
        
        Args:
            error: The error to log
            context: Additional context information
        """
        self.error_count += 1
        self.last_error = error
        
        error_details = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'stack_trace': traceback.format_exc(),
            **(context or {})
        }
        
        logger.error(
            "Error occurred",
            extra={
                'error': str(error),
                'details': error_details
            }
        )
        
    def setup_error_handling(self, bot: discord.Client) -> None:
        """
        Set up global error handling for the bot.
        
        Args:
            bot: The Discord bot instance
        """
        @bot.event
        async def on_error(event: str, *args, **kwargs):
            error = traceback.format_exc()
            logger.error(
                f"Event error",
                extra={
                    'event': event,
                    'error': error,
                    'args': args,
                    'kwargs': kwargs
                }
            )
            
        logger.info("Error handling system initialized") 