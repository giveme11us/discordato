"""
path: core/error_handler.py
purpose: Handles errors and exceptions across the bot
critical:
- Provides centralized error handling
- Logs errors appropriately
- Sends user-friendly error messages
"""

import logging
import traceback
from typing import Optional, Dict, Any
import discord
from discord import app_commands
from discord.app_commands import errors

logger = logging.getLogger('core.error_handler')

class BotError(Exception):
    """Base exception class for all bot errors."""
    def __init__(self, message: str, user_message: Optional[str] = None):
        super().__init__(message)
        self.user_message = user_message or message

class CommandError(BotError):
    """Raised when a command fails to execute properly."""
    pass

class PermissionError(BotError):
    """Raised when a user lacks required permissions."""
    pass

class ConfigurationError(BotError):
    """Raised when there's an issue with bot configuration."""
    pass

class ValidationError(BotError):
    """Raised when input validation fails."""
    pass

class DatabaseError(BotError):
    """Raised when a database operation fails."""
    pass

class ErrorHandler:
    """Handles errors and exceptions across the bot."""
    
    def __init__(self, bot):
        self.bot = bot
        logger.info("Error handling system initialized")
        
        # Set up error handlers
        bot.tree.on_error = self.on_app_command_error
        
    async def on_app_command_error(self, interaction: discord.Interaction, error: errors.AppCommandError):
        """
        Handle errors from application commands.
        
        Args:
            interaction: The interaction that caused the error
            error: The error that occurred
        """
        if isinstance(error, errors.CheckFailure):
            # This is an expected error when permission checks fail
            # The decorator already sent an ephemeral message to the user
            logger.debug(
                f"Permission check failed for command '{interaction.command.name}' "
                f"used by {interaction.user} (ID: {interaction.user.id})"
            )
            return
            
        # Handle other command errors
        try:
            if interaction.response.is_done():
                await interaction.followup.send(
                    "An error occurred while processing your command.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "An error occurred while processing your command.",
                    ephemeral=True
                )
        except Exception as e:
            logger.error(f"Error sending error message: {e}")
            
        # Log the full error
        logger.error(
            f"Error in command '{interaction.command.name if interaction.command else 'unknown'}': {error}",
            exc_info=error
        )

async def handle_interaction_error(
    interaction: discord.Interaction,
    error: Exception,
    **kwargs: Dict[str, Any]
) -> None:
    """
    Handle errors that occur during command execution.
    
    Args:
        interaction: The Discord interaction
        error: The exception that occurred
        **kwargs: Additional context for error handling
    """
    error_message = "An error occurred while processing your request."
    is_ephemeral = True
    
    try:
        if isinstance(error, app_commands.CommandOnCooldown):
            error_message = f"This command is on cooldown. Try again in {error.retry_after:.1f} seconds."
            
        elif isinstance(error, app_commands.MissingPermissions):
            error_message = "You don't have permission to use this command."
            
        elif isinstance(error, PermissionError):
            error_message = error.user_message or "You don't have permission to perform this action."
            
        elif isinstance(error, ValidationError):
            error_message = error.user_message or "Invalid input provided."
            
        elif isinstance(error, CommandError):
            error_message = error.user_message or "Failed to execute command."
            
        elif isinstance(error, ConfigurationError):
            error_message = "A configuration error has occurred. Please contact an administrator."
            logger.error(f"Configuration error: {str(error)}", exc_info=error)
            
        elif isinstance(error, DatabaseError):
            error_message = "A database error has occurred. Please try again later."
            logger.error(f"Database error: {str(error)}", exc_info=error)
            
        else:
            logger.error(f"Unhandled error: {str(error)}", exc_info=error)
            
        # Log detailed error information
        logger.error(
            f"Error in {interaction.command.name if interaction.command else 'unknown command'}: "
            f"{str(error)}\n"
            f"User: {interaction.user} ({interaction.user.id})\n"
            f"Guild: {interaction.guild.name if interaction.guild else 'DM'} "
            f"({interaction.guild_id if interaction.guild else 'N/A'})\n"
            f"Additional context: {kwargs}"
        )
        
        # Send error message to user
        if not interaction.response.is_done():
            await interaction.response.send_message(
                error_message,
                ephemeral=is_ephemeral
            )
        else:
            await interaction.followup.send(
                error_message,
                ephemeral=is_ephemeral
            )
            
    except Exception as e:
        # If error handling itself fails, log it and try to notify user
        logger.critical(f"Error handler failed: {str(e)}", exc_info=e)
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "An unexpected error occurred.",
                    ephemeral=True
                )
        except:
            pass  # At this point, we can't do anything else

def setup_error_handling(bot: discord.Client) -> None:
    """
    Set up global error handlers for the bot.
    
    Args:
        bot: The Discord bot instance
    """
    @bot.event
    async def on_error(event: str, *args, **kwargs):
        """Handle non-command errors."""
        error = traceback.format_exc()
        logger.error(f"Error in {event}: {error}")
        
    logger.info("Error handling system initialized") 