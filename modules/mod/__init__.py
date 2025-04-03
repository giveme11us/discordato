"""
path: modules/mod/__init__.py
purpose: Provides moderation and utility commands
critical:
- Manages command groups for moderation
- Handles role-based access control
- Provides utility functions
"""

import os
import logging
import discord
from discord import app_commands
from discord.ext import commands
from functools import wraps

logger = logging.getLogger('discord_bot.mod')

# Configuration
MOD_WHITELIST_ROLE_IDS = [int(id) for id in os.getenv('MOD_WHITELIST_ROLE_IDS', '').split(',') if id]
PINGER_USER_ROLE_ID = int(os.getenv('PINGER_USER_ROLE_ID', '0'))

# Track loaded submodules
loaded_submodules = set()

def require_mod_role():
    """
    Decorator to check if user has a moderator role.
    
    Returns:
        function: Decorated function that checks for mod role
    """
    async def predicate(interaction: discord.Interaction) -> bool:
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
            
        # Check if user has any of the whitelisted roles
        has_role = any(role.id in MOD_WHITELIST_ROLE_IDS for role in interaction.user.roles)
        
        if not has_role:
            await interaction.response.send_message(
                "You need moderator permissions to use this command.",
                ephemeral=True
            )
            return False
            
        return True
        
    return app_commands.check(predicate)

def require_pinger_user_role():
    """
    Decorator to check if user has the pinger user role.
    This allows users to manage their own pinger settings.
    
    Returns:
        function: Decorated function that checks for pinger user role
    """
    async def predicate(interaction: discord.Interaction) -> bool:
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
            
        # Check if user has the pinger user role
        has_role = any(role.id == PINGER_USER_ROLE_ID for role in interaction.user.roles)
        
        if not has_role:
            await interaction.response.send_message(
                "You need the pinger user role to use this command.",
                ephemeral=True
            )
            return False
            
        return True
        
    return app_commands.check(predicate)

async def setup(bot, registered_commands=None):
    """
    Set up the mod module.
    
    Args:
        bot: The Discord bot instance
        registered_commands: Set of already registered commands
    
    Returns:
        Set[str]: Updated set of registered commands
    """
    # Initialize registered_commands if not provided
    if registered_commands is None:
        registered_commands = set()
        
    # Register general command if not already registered
    if 'general' not in registered_commands:
        @bot.tree.command(
            name="general",
            description="View bot status and configuration"
        )
        @require_mod_role()
        async def general(interaction: discord.Interaction):
            """View bot status and configuration."""
            # Create status embed
            embed = discord.Embed(
                title="Bot Status & Configuration",
                color=int(os.getenv('EMBED_COLOR', '000000'), 16)
            )
            
            # Bot Info
            bot_info = (
                f"**Latency:** {round(bot.latency * 1000)}ms\n"
                f"**Guilds:** {len(bot.guilds)}\n"
                f"**Development Mode:** {os.getenv('DEVELOPMENT', 'false')}\n"
                f"**Debug Mode:** {os.getenv('DEBUG', 'false')}"
            )
            embed.add_field(name="Bot Info", value=bot_info, inline=False)
            
            # Module Status
            module_status = (
                f"**Enabled Modules:** {', '.join(os.getenv('ENABLED_MODULES', '').split(','))}\n"
                f"**Loaded Submodules:** {', '.join(loaded_submodules)}"
            )
            embed.add_field(name="Module Status", value=module_status, inline=False)
            
            # Mod Configuration
            mod_config = (
                f"**Mod Roles:** {', '.join(str(id) for id in MOD_WHITELIST_ROLE_IDS)}\n"
                f"**Command Cooldown:** {os.getenv('COMMAND_COOLDOWN', '3')}s\n"
                f"**Rate Limit:** {os.getenv('MAX_COMMANDS_PER_MINUTE', '60')} commands/minute"
            )
            embed.add_field(name="Mod Configuration", value=mod_config, inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        registered_commands.add('general')
        logger.info("Registered command: general")
        
    # Load submodules
    submodules = ['pinger', 'reaction']
    for submodule in submodules:
        try:
            if submodule not in loaded_submodules:
                module = __import__(f"modules.mod.{submodule}", fromlist=["setup"])
                if hasattr(module, "setup"):
                    await module.setup(bot)
                    loaded_submodules.add(submodule)
                    logger.info(f"Loaded submodule: {submodule}")
        except Exception as e:
            logger.error(f"Error loading submodule {submodule}: {e}")
            
    return registered_commands

async def teardown(bot):
    """Clean up the mod module."""
    # Unload submodules
    for submodule in loaded_submodules.copy():
        try:
            module = __import__(f"modules.mod.{submodule}", fromlist=["teardown"])
            if hasattr(module, "teardown"):
                await module.teardown(bot)
                loaded_submodules.remove(submodule)
                logger.info(f"Unloaded submodule: {submodule}")
        except Exception as e:
            logger.error(f"Error unloading submodule {submodule}: {e}") 