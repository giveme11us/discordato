"""
Pinger Configuration Command

This module provides a command to configure the pinger feature.
"""

import logging
import discord
from discord import app_commands
from config import pinger_config

logger = logging.getLogger('discord_bot.modules.mod.pinger.config_cmd')

async def config_command(interaction, setting=None, value=None):
    """
    Pinger configuration command handler.
    
    Args:
        interaction: The Discord interaction
        setting: The setting to view or modify
        value: The new value for the setting
    """
    # Check if user has administrator permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You need administrator permissions to use this command.", ephemeral=True)
        return
    
    if not setting:
        # Show all settings
        embed = discord.Embed(
            title="Pinger Configuration",
            description="Current configuration settings for the pinger feature",
            color=discord.Color.blue()
        )
        
        # Add settings to the embed
        embed.add_field(
            name="Notification Channel",
            value=f"<#{pinger_config.NOTIFICATION_CHANNEL_ID}>" if pinger_config.NOTIFICATION_CHANNEL_ID else "Not set",
            inline=False
        )
        
        whitelist_roles = []
        for role_id in pinger_config.WHITELIST_ROLE_IDS:
            role = interaction.guild.get_role(role_id)
            if role:
                whitelist_roles.append(role.mention)
        
        embed.add_field(
            name="Whitelist Roles",
            value=", ".join(whitelist_roles) if whitelist_roles else "None",
            inline=False
        )
        
        embed.add_field(
            name="Monitor @everyone",
            value="Enabled" if pinger_config.MONITOR_EVERYONE else "Disabled",
            inline=True
        )
        
        embed.add_field(
            name="Monitor @here",
            value="Enabled" if pinger_config.MONITOR_HERE else "Disabled",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
        return
    
    # View or set a specific setting
    if setting.lower() == "channel":
        if not value:
            # Show current channel
            if pinger_config.NOTIFICATION_CHANNEL_ID:
                channel = interaction.guild.get_channel(pinger_config.NOTIFICATION_CHANNEL_ID)
                if channel:
                    await interaction.response.send_message(f"Current notification channel: {channel.mention}")
                else:
                    await interaction.response.send_message("Current notification channel ID is set but the channel could not be found.")
            else:
                await interaction.response.send_message("Notification channel is not set.")
        else:
            # Change setting in production would require writing to .env or database
            # This is just a simulation for the example
            await interaction.response.send_message(f"This would set the notification channel to the specified channel. In a real implementation, this would update the .env file or database.")
    
    elif setting.lower() == "whitelist":
        if not value:
            # Show current whitelist
            whitelist_roles = []
            for role_id in pinger_config.WHITELIST_ROLE_IDS:
                role = interaction.guild.get_role(role_id)
                if role:
                    whitelist_roles.append(role.mention)
            
            if whitelist_roles:
                await interaction.response.send_message(f"Current whitelist roles: {', '.join(whitelist_roles)}")
            else:
                await interaction.response.send_message("No whitelist roles are currently set.")
        else:
            # Change setting in production would require writing to .env or database
            await interaction.response.send_message(f"This would add or remove the specified role from the whitelist. In a real implementation, this would update the .env file or database.")
    
    elif setting.lower() in ["everyone", "here"]:
        if not value:
            # Show current setting
            if setting.lower() == "everyone":
                enabled = pinger_config.MONITOR_EVERYONE
            else:
                enabled = pinger_config.MONITOR_HERE
                
            await interaction.response.send_message(f"Monitoring for @{setting.lower()} is currently {'enabled' if enabled else 'disabled'}.")
        else:
            # Change setting in production would require writing to .env or database
            await interaction.response.send_message(f"This would {'enable' if value.lower() == 'true' else 'disable'} monitoring for @{setting.lower()}. In a real implementation, this would update the .env file or database.")
    
    else:
        await interaction.response.send_message(f"Unknown setting: {setting}", ephemeral=True)

def setup_config_cmd(bot):
    """
    Register the pinger configuration command with the bot.
    
    Args:
        bot: The Discord bot instance
    """
    @bot.tree.command(
        name="pinger-config",
        description="Configure the pinger feature"
    )
    @app_commands.describe(
        setting="The setting to view or modify (channel, whitelist, everyone, here)",
        value="The new value for the setting"
    )
    async def pinger_config(interaction: discord.Interaction, setting: str = None, value: str = None):
        await config_command(interaction, setting, value)
    
    logger.debug("Registered pinger-config command") 