"""
Pinger Configuration Command

This module provides a command to configure the pinger feature.
"""

import logging
import discord
import os
import re
from pathlib import Path
from discord import app_commands
from config import pinger_config
from config import embed_config

logger = logging.getLogger('discord_bot.modules.mod.pinger.config_cmd')

async def update_env_value(key, value):
    """
    Update a value in the .env file.
    
    Args:
        key: The environment variable key
        value: The new value to set
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Find the .env file
        env_path = Path('.env')
        if not env_path.exists():
            logger.error(".env file not found")
            return False
        
        # Read the .env file
        with open(env_path, 'r') as file:
            lines = file.readlines()
        
        # Find and update the specified key
        pattern = re.compile(f'^{key}=.*$')
        updated = False
        
        for i, line in enumerate(lines):
            if pattern.match(line):
                lines[i] = f"{key}={value}\n"
                updated = True
                break
        
        # If the key doesn't exist, add it to the end
        if not updated:
            lines.append(f"{key}={value}\n")
        
        # Write the updated content back to the .env file
        with open(env_path, 'w') as file:
            file.writelines(lines)
        
        logger.info(f"Updated {key} in .env file to {value}")
        return True
    
    except Exception as e:
        logger.error(f"Error updating .env file: {str(e)}")
        return False

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
        # Make initial configuration display ephemeral
        await interaction.response.defer(ephemeral=True)
        
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
        
        embed.add_field(
            name="Monitor role mentions",
            value="Enabled" if pinger_config.MONITOR_ROLES else "Disabled",
            inline=True
        )
        
        # Add usage help to the embed
        embed.add_field(
            name="Command Usage",
            value=(
                "**Available settings:**\n"
                "• `/pinger-config channel #channel-name` - Set notification channel\n"
                "• `/pinger-config whitelist add @role` - Add role to whitelist\n"
                "• `/pinger-config whitelist remove @role` - Remove role from whitelist\n"
                "• `/pinger-config whitelist clear` - Clear entire whitelist\n"
                "• `/pinger-config everyone true|false` - Enable/disable @everyone monitoring\n"
                "• `/pinger-config here true|false` - Enable/disable @here monitoring\n"
                "• `/pinger-config roles true|false` - Enable/disable role mention monitoring"
            ),
            inline=False
        )
        
        # Apply default styling
        embed = embed_config.apply_default_styling(embed)
        
        await interaction.followup.send(embed=embed)
        return
    
    # View or set a specific setting
    if setting.lower() == "channel":
        if not value:
            # Show current channel with guidance for setting
            await interaction.response.defer(ephemeral=True)
            if pinger_config.NOTIFICATION_CHANNEL_ID:
                channel = interaction.guild.get_channel(pinger_config.NOTIFICATION_CHANNEL_ID)
                if channel:
                    await interaction.followup.send(
                        f"Current notification channel: {channel.mention}\n\n"
                        f"**To change it:** `/pinger-config channel #channel-name`"
                    )
                else:
                    await interaction.followup.send(
                        "Current notification channel ID is set but the channel could not be found.\n\n"
                        f"**To change it:** `/pinger-config channel #channel-name`"
                    )
            else:
                await interaction.followup.send(
                    "Notification channel is not set.\n\n"
                    f"**To set it:** `/pinger-config channel #channel-name`"
                )
        else:
            # Try to extract channel ID from mention or direct input
            if value.startswith('<#') and value.endswith('>'):
                # Extract from mention format <#123456789>
                channel_id = value[2:-1]
            else:
                # Assume direct ID input
                channel_id = value
            
            # Validate channel ID
            if not channel_id.isdigit():
                await interaction.response.send_message("Invalid channel ID format. Please provide a valid channel ID or mention.", ephemeral=True)
                return
            
            channel = interaction.guild.get_channel(int(channel_id))
            if not channel:
                await interaction.response.send_message("Channel not found. Please provide a valid channel ID or mention.", ephemeral=True)
                return
            
            # Update the .env file
            await interaction.response.defer(ephemeral=True)
            success = await update_env_value('PINGER_NOTIFICATION_CHANNEL_ID', channel_id)
            
            if success:
                # Update the variable in memory
                pinger_config.NOTIFICATION_CHANNEL_ID = int(channel_id)
                await interaction.followup.send(f"Notification channel updated to {channel.mention}. The changes will take effect immediately, but will also persist after restart.")
            else:
                await interaction.followup.send("Failed to update the notification channel. Check the logs for more information.")
    
    elif setting.lower() == "whitelist":
        if not value:
            # Show current whitelist with guidance
            await interaction.response.defer(ephemeral=True)
            whitelist_roles = []
            for role_id in pinger_config.WHITELIST_ROLE_IDS:
                role = interaction.guild.get_role(role_id)
                if role:
                    whitelist_roles.append(role.mention)
            
            usage_help = (
                "\n\n**Available commands:**\n"
                "• `/pinger-config whitelist add @role` - Add role to whitelist\n"
                "• `/pinger-config whitelist remove @role` - Remove role from whitelist\n"
                "• `/pinger-config whitelist clear` - Clear entire whitelist"
            )
            
            if whitelist_roles:
                await interaction.followup.send(f"Current whitelist roles: {', '.join(whitelist_roles)}{usage_help}")
            else:
                await interaction.followup.send(f"No whitelist roles are currently set.{usage_help}")
        else:
            await interaction.response.defer(ephemeral=True)
            
            # Parse the command - value can be "add <role>" or "remove <role>" or "clear"
            parts = value.split(maxsplit=1)
            command = parts[0].lower() if parts else ""
            
            if command == "clear":
                # Clear the whitelist
                success = await update_env_value('PINGER_WHITELIST_ROLE_IDS', "")
                
                if success:
                    # Update the variable in memory
                    pinger_config.WHITELIST_ROLE_IDS = []
                    await interaction.followup.send("Whitelist has been cleared. The changes will take effect immediately, but will also persist after restart.")
                else:
                    await interaction.followup.send("Failed to clear the whitelist. Check the logs for more information.")
                return
            
            if len(parts) < 2:
                await interaction.followup.send(
                    "Invalid command format. Use one of the following:\n"
                    "• `/pinger-config whitelist add @role`\n"
                    "• `/pinger-config whitelist remove @role`\n"
                    "• `/pinger-config whitelist clear`", 
                    ephemeral=True
                )
                return
            
            role_value = parts[1]
            
            # Try to extract role ID from mention or direct input
            if role_value.startswith('<@&') and role_value.endswith('>'):
                # Extract from mention format <@&123456789>
                role_id = role_value[3:-1]
            else:
                # Assume direct ID input
                role_id = role_value
            
            # Validate role ID
            if not role_id.isdigit():
                await interaction.followup.send("Invalid role ID format. Please provide a valid role ID or mention.", ephemeral=True)
                return
            
            role = interaction.guild.get_role(int(role_id))
            if not role:
                await interaction.followup.send("Role not found. Please provide a valid role ID or mention.", ephemeral=True)
                return
            
            # Get current whitelist from the config
            current_whitelist = pinger_config.WHITELIST_ROLE_IDS.copy()
            role_id_int = int(role_id)
            
            if command == "add":
                # Add role to whitelist if not already there
                if role_id_int not in current_whitelist:
                    current_whitelist.append(role_id_int)
                    
                    # Update the .env file
                    new_value = ",".join(str(id) for id in current_whitelist)
                    success = await update_env_value('PINGER_WHITELIST_ROLE_IDS', new_value)
                    
                    if success:
                        # Update the variable in memory
                        pinger_config.WHITELIST_ROLE_IDS = current_whitelist
                        await interaction.followup.send(f"Added {role.mention} to the whitelist. The changes will take effect immediately, but will also persist after restart.")
                    else:
                        await interaction.followup.send("Failed to update the whitelist. Check the logs for more information.")
                else:
                    await interaction.followup.send(f"{role.mention} is already in the whitelist.")
            
            elif command == "remove":
                # Remove role from whitelist if it's there
                if role_id_int in current_whitelist:
                    current_whitelist.remove(role_id_int)
                    
                    # Update the .env file
                    new_value = ",".join(str(id) for id in current_whitelist)
                    success = await update_env_value('PINGER_WHITELIST_ROLE_IDS', new_value)
                    
                    if success:
                        # Update the variable in memory
                        pinger_config.WHITELIST_ROLE_IDS = current_whitelist
                        await interaction.followup.send(f"Removed {role.mention} from the whitelist. The changes will take effect immediately, but will also persist after restart.")
                    else:
                        await interaction.followup.send("Failed to update the whitelist. Check the logs for more information.")
                else:
                    await interaction.followup.send(f"{role.mention} is not in the whitelist.")
            
            else:
                await interaction.followup.send(
                    "Invalid command. Use one of the following:\n"
                    "• `/pinger-config whitelist add @role`\n"
                    "• `/pinger-config whitelist remove @role`\n"
                    "• `/pinger-config whitelist clear`", 
                    ephemeral=True
                )
    
    elif setting.lower() in ["everyone", "here", "roles"]:
        if not value:
            # Show current setting with guidance
            await interaction.response.defer(ephemeral=True)
            if setting.lower() == "everyone":
                enabled = pinger_config.MONITOR_EVERYONE
                setting_name = "@everyone"
            elif setting.lower() == "here":
                enabled = pinger_config.MONITOR_HERE
                setting_name = "@here"
            else:  # roles
                enabled = pinger_config.MONITOR_ROLES
                setting_name = "role mentions"
                
            await interaction.followup.send(
                f"Monitoring for {setting_name} is currently **{'enabled' if enabled else 'disabled'}**.\n\n"
                f"**To change it:** `/pinger-config {setting.lower()} {'false' if enabled else 'true'}`"
            )
        else:
            # Check if value is true/false
            if value.lower() not in ['true', 'false']:
                await interaction.response.send_message(
                    "Value must be 'true' or 'false'.\n\n"
                    f"Example: `/pinger-config {setting.lower()} true`", 
                    ephemeral=True
                )
                return
            
            # Get the corresponding env var name
            if setting.lower() == "everyone":
                env_key = "PINGER_MONITOR_EVERYONE"
                config_var = "MONITOR_EVERYONE"
                setting_name = "@everyone"
            elif setting.lower() == "here":
                env_key = "PINGER_MONITOR_HERE"
                config_var = "MONITOR_HERE"
                setting_name = "@here"
            else:  # roles
                env_key = "PINGER_MONITOR_ROLES"
                config_var = "MONITOR_ROLES"
                setting_name = "role mentions"
            
            # Update the .env file
            await interaction.response.defer(ephemeral=True)
            success = await update_env_value(env_key, value)
            
            if success:
                # Update the variable in memory
                new_value = value.lower() == 'true'
                setattr(pinger_config, config_var, new_value)
                await interaction.followup.send(f"Monitoring for {setting_name} has been **{'enabled' if new_value else 'disabled'}**. The changes will take effect immediately, but will also persist after restart.")
            else:
                await interaction.followup.send(f"Failed to update monitoring setting for {setting_name}. Check the logs for more information.")
    
    else:
        # Provide helpful guidance for unknown settings
        await interaction.response.send_message(
            f"Unknown setting: `{setting}`\n\n"
            "**Available settings:**\n"
            "• `channel` - Configure notification channel\n"
            "• `whitelist` - Manage whitelist roles\n"
            "• `everyone` - Toggle @everyone monitoring\n"
            "• `here` - Toggle @here monitoring\n"
            "• `roles` - Toggle role mentions monitoring",
            ephemeral=True
        )

def setup_config_cmd(bot):
    """
    Register the pinger-config slash command.
    
    Args:
        bot: The Discord bot instance
    """
    logger.info("Registering pinger-config command")
    
    # Import the permission decorator
    from utils.permissions import mod_only
    
    @bot.tree.command(
        name="pinger-config",
        description="Configure the mention notifications feature"
    )
    @app_commands.describe(
        setting="The setting to view or modify (channel, everyone, here, roles, whitelist)",
        action="The action to perform for whitelist (add, remove, clear, view)",
        value="The value for the action"
    )
    @mod_only()
    async def pinger_config(interaction: discord.Interaction, setting: str = None, action: str = None, value: str = None):
        await handle_pinger_config(interaction, setting, action, value)
        
    logger.info("Registered pinger-config command") 