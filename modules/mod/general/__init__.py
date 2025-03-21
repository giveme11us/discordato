"""
path: modules/mod/general/__init__.py
purpose: Implements basic moderation commands
critical:
- Requires proper permissions
- Handles message and user management
- Provides audit logging
"""

import os
import logging
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

logger = logging.getLogger('discord_bot.mod.general')

async def setup(bot):
    """
    Set up the general moderation module.
    
    Args:
        bot: The Discord bot instance
    """
    # Register general command
    @bot.tree.command(
        name="general",
        description="View bot status and configuration"
    )
    async def general(interaction: discord.Interaction):
        # Check if user has moderator role
        if not any(role.id in bot.config.MOD_WHITELIST_ROLE_IDS for role in interaction.user.roles):
            await interaction.response.send_message(
                "You need moderator permissions to use this command.",
                ephemeral=True
            )
            return
        
        # Create status embed
        embed = discord.Embed(
            title="Bot Status & Configuration",
            color=int(os.getenv('EMBED_COLOR', '000000'), 16)
        )
        
        # Add bot info
        embed.add_field(
            name="Bot Info",
            value=f"Latency: {round(bot.latency * 1000)}ms\nGuilds: {len(bot.guilds)}",
            inline=False
        )
        
        # Add enabled modules
        enabled_modules = os.getenv('ENABLED_MODULES', '').split(',')
        embed.add_field(
            name="Enabled Modules",
            value='\n'.join(enabled_modules) if enabled_modules else "None",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # Register help command
    @bot.tree.command(
        name="help",
        description="Display help information"
    )
    @app_commands.describe(
        command="The command to get help for"
    )
    async def help(
        interaction: discord.Interaction,
        command: Optional[str] = None
    ):
        embed = discord.Embed(
            title="Command Help",
            color=int(os.getenv('EMBED_COLOR', '000000'), 16)
        )
        
        if command:
            # Show specific command help
            if command == "general":
                embed.add_field(
                    name="/general",
                    value="View bot status and configuration\nPermissions: Moderator",
                    inline=False
                )
            elif command == "help":
                embed.add_field(
                    name="/help [command]",
                    value="Display help information\nPermissions: Everyone",
                    inline=False
                )
            elif command == "ping":
                embed.add_field(
                    name="/ping",
                    value="Check bot latency\nPermissions: Everyone",
                    inline=False
                )
            else:
                embed.description = "Command not found."
        else:
            # Show general help
            embed.add_field(
                name="General Commands",
                value=(
                    "`/general` - View bot status and configuration\n"
                    "`/help [command]` - Display help information\n"
                    "`/ping` - Check bot latency"
                ),
                inline=False
            )
            
            # Show moderation commands if user has permissions
            if any(role.id in bot.config.MOD_WHITELIST_ROLE_IDS for role in interaction.user.roles):
                embed.add_field(
                    name="Moderation Commands",
                    value=(
                        "`/keyword` - Manage keyword filters\n"
                        "`/reaction` - Manage reaction settings\n"
                        "`/pinger` - Configure ping monitoring"
                    ),
                    inline=False
                )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # Register ping command
    @bot.tree.command(
        name="ping",
        description="Check bot latency"
    )
    async def ping(interaction: discord.Interaction):
        latency = round(bot.latency * 1000)
        await interaction.response.send_message(
            f"Pong! {latency}ms",
            ephemeral=True
        )
    
    logger.info("Registered general commands")

async def teardown(bot):
    """Clean up the general module."""
    pass 