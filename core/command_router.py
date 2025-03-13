"""
Command Router

This module handles routing commands to the appropriate module handlers.
"""

import logging
from discord.ext import commands
from config import settings

logger = logging.getLogger('discord_bot.command_router')

class CommandRouter:
    """
    Routes commands to the appropriate module handlers.
    Used primarily in single-bot mode to direct commands to their respective modules.
    """
    
    def __init__(self):
        """
        Initialize the command router.
        """
        self.routes = {}
    
    def register_route(self, command_name, module_name, handler):
        """
        Register a command route.
        
        Args:
            command_name (str): The name of the command
            module_name (str): The name of the module
            handler (callable): The function to handle the command
        """
        self.routes[command_name] = {
            'module': module_name,
            'handler': handler
        }
        logger.debug(f"Registered route for command '{command_name}' to module '{module_name}'")
    
    async def route_command(self, ctx, command_name, *args, **kwargs):
        """
        Route a command to its handler.
        
        Args:
            ctx: The command context
            command_name (str): The name of the command
            *args: Positional arguments for the command
            **kwargs: Keyword arguments for the command
        
        Returns:
            The result of the command handler
        """
        if command_name not in self.routes:
            logger.warning(f"No route found for command '{command_name}'")
            await ctx.send(settings.ERROR_MESSAGES['command_not_found'].format(
                prefix=settings.COMMAND_PREFIX
            ))
            return None
        
        route = self.routes[command_name]
        logger.debug(f"Routing command '{command_name}' to module '{route['module']}'")
        
        try:
            return await route['handler'](ctx, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error executing command '{command_name}': {str(e)}")
            await ctx.send(settings.ERROR_MESSAGES['general_error'])
            return None
    
    def setup_error_handlers(self, bot):
        """
        Set up error handlers for the bot.
        
        Args:
            bot: The Discord bot instance
        """
        @bot.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.CommandNotFound):
                await ctx.send(settings.ERROR_MESSAGES['command_not_found'].format(
                    prefix=settings.COMMAND_PREFIX
                ))
            elif isinstance(error, commands.MissingPermissions):
                await ctx.send(settings.ERROR_MESSAGES['permission_denied'])
            elif isinstance(error, commands.CommandOnCooldown):
                await ctx.send(settings.ERROR_MESSAGES['cooldown'].format(
                    time=int(error.retry_after)
                ))
            else:
                logger.error(f"Command error: {str(error)}")
                await ctx.send(settings.ERROR_MESSAGES['general_error']) 