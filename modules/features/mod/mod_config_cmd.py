"""
Mod Configuration Command

This module provides a slash command to configure module-wide settings.
"""

import logging
import os
import discord
from discord import app_commands
from discord.ext import commands
from config.features.moderation import mod
from config.features.embed_config import embed as embed_config
from utils.permissions import mod_only

logger = logging.getLogger('discord_bot.modules.mod.mod_config_cmd')

async def update_env_file(key, value):
    """
    Update a value in the .env file.
    
    Args:
        key: The key to update
        value: The new value
    """
    env_path = '.env'
    
    # Read the current .env file
    with open(env_path, 'r') as file:
        lines = file.readlines()
    
    # Find and update the specified key
    key_found = False
    for i, line in enumerate(lines):
        if line.strip() and not line.strip().startswith('#'):
            if line.split('=')[0].strip() == key:
                lines[i] = f"{key}={value}\n"
                key_found = True
                break
    
    # If key wasn't found, add it
    if not key_found:
        lines.append(f"{key}={value}\n")
    
    # Write the updated content back to the .env file
    with open(env_path, 'w') as file:
        file.writelines(lines)

async def handle_mod_config(interaction, setting=None, action=None, value=None):
    """
    Handle the mod-config command.
    
    Args:
        interaction: The Discord interaction
        setting: The setting to configure (whitelist)
        action: The action to perform (add, remove, clear, view)
        value: The value for the action
    """
    # Only allow administrators to use this command
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "You need administrator permissions to use this command.",
            ephemeral=True
        )
        return
    
    # If no setting specified, show current configuration
    if not setting:
        # Create an embed with the current configuration
        embed = discord.Embed(
            title="Mod Module Configuration",
            description="Current module-wide settings",
            color=discord.Color.blue()
        )
        
        # Format the whitelist role IDs
        if mod.WHITELIST_ROLE_IDS:
            whitelist_roles_str = "\n".join([f"• <@&{role_id}>" for role_id in mod.WHITELIST_ROLE_IDS])
        else:
            whitelist_roles_str = "No whitelist configured"
            
        embed.add_field(
            name="Whitelisted Roles",
            value=whitelist_roles_str,
            inline=False
        )
        
        # Add instructions for updating
        embed.add_field(
            name="How to Update",
            value="Use `/mod-config [setting] [action] [value]`\n"
                  "Settings: `whitelist`\n"
                  "Actions: `add`, `remove`, `clear`\n"
                  "Example: `/mod-config whitelist add @role`",
            inline=False
        )
        
        # Apply default styling
        embed = embed_config.apply_default_styling(embed)
        
        await interaction.response.send_message(embed=embed)
        return
    
    # Handle whitelist settings
    if setting.lower() == "whitelist":
        if not action:
            await interaction.response.send_message(
                "Please provide an action: add, remove, clear, or view",
                ephemeral=True
            )
            return
        
        # Handle different actions
        if action.lower() == "view":
            # Format the whitelist role IDs
            if mod.WHITELIST_ROLE_IDS:
                whitelist_roles_str = "\n".join([f"• <@&{role_id}> (ID: {role_id})" for role_id in mod.WHITELIST_ROLE_IDS])
            else:
                whitelist_roles_str = "No whitelist configured"
                
            await interaction.response.send_message(
                f"**Current Whitelist Roles:**\n{whitelist_roles_str}",
                ephemeral=True
            )
            return
            
        elif action.lower() == "add":
            if not value:
                await interaction.response.send_message(
                    "Please provide a role mention or ID to add to the whitelist",
                    ephemeral=True
                )
                return
            
            # Extract role ID from mention or direct ID
            role_id = None
            if value.startswith('<@&') and value.endswith('>'):
                # Extract ID from mention
                role_id_str = value[3:-1]
                try:
                    role_id = int(role_id_str)
                except ValueError:
                    await interaction.response.send_message(
                        f"Invalid role mention: {value}",
                        ephemeral=True
                    )
                    return
            else:
                # Try direct ID
                try:
                    role_id = int(value)
                except ValueError:
                    await interaction.response.send_message(
                        f"Invalid role ID: {value}. Please use a role mention or numeric ID.",
                        ephemeral=True
                    )
                    return
            
            # Verify role exists
            role = interaction.guild.get_role(role_id)
            if not role:
                await interaction.response.send_message(
                    f"Role with ID {role_id} not found in this server.",
                    ephemeral=True
                )
                return
            
            # Update the whitelist
            current_whitelist = list(mod.WHITELIST_ROLE_IDS)
            if role_id in current_whitelist:
                await interaction.response.send_message(
                    f"Role {role.name} is already in the whitelist.",
                    ephemeral=True
                )
                return
            
            current_whitelist.append(role_id)
            whitelist_str = ",".join(str(id) for id in current_whitelist)
            
            # Update the .env file
            await update_env_file('MOD_WHITELIST_ROLE_IDS', whitelist_str)
            
            # Update the in-memory config
            mod.WHITELIST_ROLE_IDS = current_whitelist
            
            await interaction.response.send_message(
                f"Added role {role.name} to the module whitelist.",
                ephemeral=True
            )
        
        elif action.lower() == "remove":
            if not value:
                await interaction.response.send_message(
                    "Please provide a role mention or ID to remove from the whitelist",
                    ephemeral=True
                )
                return
            
            # Extract role ID from mention or direct ID
            role_id = None
            if value.startswith('<@&') and value.endswith('>'):
                # Extract ID from mention
                role_id_str = value[3:-1]
                try:
                    role_id = int(role_id_str)
                except ValueError:
                    await interaction.response.send_message(
                        f"Invalid role mention: {value}",
                        ephemeral=True
                    )
                    return
            else:
                # Try direct ID
                try:
                    role_id = int(value)
                except ValueError:
                    await interaction.response.send_message(
                        f"Invalid role ID: {value}. Please use a role mention or numeric ID.",
                        ephemeral=True
                    )
                    return
            
            # Update the whitelist
            current_whitelist = list(mod.WHITELIST_ROLE_IDS)
            if role_id not in current_whitelist:
                role_name = interaction.guild.get_role(role_id).name if interaction.guild.get_role(role_id) else f"ID {role_id}"
                await interaction.response.send_message(
                    f"Role {role_name} is not in the whitelist.",
                    ephemeral=True
                )
                return
            
            current_whitelist.remove(role_id)
            whitelist_str = ",".join(str(id) for id in current_whitelist)
            
            # Update the .env file
            await update_env_file('MOD_WHITELIST_ROLE_IDS', whitelist_str)
            
            # Update the in-memory config
            mod.WHITELIST_ROLE_IDS = current_whitelist
            
            role_name = interaction.guild.get_role(role_id).name if interaction.guild.get_role(role_id) else f"ID {role_id}"
            await interaction.response.send_message(
                f"Removed role {role_name} from the module whitelist.",
                ephemeral=True
            )
        
        elif action.lower() == "clear":
            # Clear the whitelist
            await update_env_file('MOD_WHITELIST_ROLE_IDS', '')
            
            # Update the in-memory config
            mod.WHITELIST_ROLE_IDS = []
            
            await interaction.response.send_message(
                "Cleared the module whitelist. All roles have been removed.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"Unknown action: {action}. Available actions: add, remove, clear, view",
                ephemeral=True
            )
    else:
        await interaction.response.send_message(
            f"Unknown setting: {setting}. Available settings: whitelist",
            ephemeral=True
        )

def setup_config_cmd(bot):
    """
    Register the mod-config slash command.
    
    Args:
        bot: The Discord bot instance
    """
    logger.info("Registering mod-config command")
    
    @bot.tree.command(
        name="mod-config",
        description="Configure module-wide settings"
    )
    @app_commands.describe(
        setting="The setting to view or modify (whitelist)",
        action="The action to perform (add, remove, clear, view)",
        value="The value for the action (role mention or ID)"
    )
    @mod_only()
    async def mod_config(
        interaction: discord.Interaction, 
        setting: str = None, 
        action: str = None, 
        value: str = None
    ):
        await handle_mod_config(interaction, setting, action, value)
        
    logger.info("Registered mod-config command") 