"""
Reaction Forward Configuration Command

This module provides a slash command to configure the reaction_forward feature.
"""

import logging
import os
import discord
from discord import app_commands
from discord.ext import commands
from config import reaction_forward_config as config
from config import embed_config

logger = logging.getLogger('discord_bot.modules.mod.reaction_forward.config_cmd')

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

class ReactionForwardConfigView(discord.ui.View):
    """
    View for configuring the reaction_forward feature.
    """
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
    
    @discord.ui.button(label="Enable", style=discord.ButtonStyle.green)
    async def enable_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Enable the feature
        await update_env_file('REACTION_FORWARD_ENABLED', 'True')
        
        # Update the config
        config.ENABLED = True
        
        # Respond to the interaction
        await interaction.response.send_message("Reaction forward feature has been enabled.", ephemeral=True)
    
    @discord.ui.button(label="Disable", style=discord.ButtonStyle.red)
    async def disable_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Disable the feature
        await update_env_file('REACTION_FORWARD_ENABLED', 'False')
        
        # Update the config
        config.ENABLED = False
        
        # Respond to the interaction
        await interaction.response.send_message("Reaction forward feature has been disabled.", ephemeral=True)

async def handle_reaction_forward_config(interaction, setting=None, value=None):
    """
    Handle the reaction-forward-config command.
    
    Args:
        interaction: The Discord interaction
        setting: The setting to configure (categories, enable, disable, forwarding, blacklist)
        value: The new value for the setting
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
            title="Reaction Forward Configuration",
            description="Current settings for the reaction forward feature",
            color=discord.Color.blue()
        )
        
        # Add fields for each setting
        embed.add_field(
            name="Enabled",
            value="✅ Yes" if config.ENABLED else "❌ No",
            inline=False
        )
        
        # Add field for forwarding feature
        embed.add_field(
            name="Message Forwarding",
            value="✅ Yes" if config.ENABLE_FORWARDING else "❌ No",
            inline=False
        )
        
        # Format the category IDs list
        if config.CATEGORY_IDS:
            category_ids_str = "\n".join([f"• {cat_id}" for cat_id in config.CATEGORY_IDS])
        else:
            category_ids_str = "No categories configured"
            
        embed.add_field(
            name="Whitelisted Categories",
            value=category_ids_str,
            inline=False
        )
        
        # Format the blacklisted channels
        if config.BLACKLIST_CHANNEL_IDS:
            blacklist_channels_str = "\n".join([f"• {chan_id}" for chan_id in config.BLACKLIST_CHANNEL_IDS])
        else:
            blacklist_channels_str = "No channels blacklisted"
            
        embed.add_field(
            name="Blacklisted Channels",
            value=blacklist_channels_str,
            inline=False
        )
        
        # Format the whitelist role IDs
        if config.WHITELIST_ROLE_IDS:
            whitelist_roles_str = "\n".join([f"• {role_id}" for role_id in config.WHITELIST_ROLE_IDS])
        else:
            whitelist_roles_str = "No whitelist configured (all users allowed)"
            
        embed.add_field(
            name="Whitelisted Roles",
            value=whitelist_roles_str + "\n\n*Note: This is shared across all mod module features*",
            inline=False
        )
        
        # Add instructions for updating
        embed.add_field(
            name="How to Update",
            value="Use `/reaction-forward-config [setting] [value]`\n"
                  "Settings: `categories`, `enable`, `disable`, `forwarding`, `blacklist`\n"
                  "Example: `/reaction-forward-config categories 123456789,987654321`\n"
                  "Example: `/reaction-forward-config blacklist 123456789,987654321`\n\n"
                  "To manage whitelist roles, use: `/mod-config whitelist [add/remove/clear] [value]`",
            inline=False
        )
        
        # Apply default styling instead of manually setting footer
        embed = embed_config.apply_default_styling(embed)
        
        # Add buttons for quick actions
        view = ReactionForwardConfigView()
        
        await interaction.response.send_message(embed=embed, view=view)
        return
    
    # Handle different settings
    if setting.lower() == "categories":
        if not value:
            await interaction.response.send_message(
                "Please provide category IDs separated by commas. Example: `123456789,987654321`",
                ephemeral=True
            )
            return
        
        # Validate the category IDs
        try:
            # Extract IDs from the comma-separated string
            category_ids = [int(cat_id.strip()) for cat_id in value.split(',') if cat_id.strip()]
            
            # Update the .env file
            await update_env_file('REACTION_FORWARD_CATEGORY_IDS', value)
            
            # Update the config
            config.CATEGORY_IDS = category_ids
            
            await interaction.response.send_message(
                f"Updated reaction forward category IDs to: {', '.join(str(cat_id) for cat_id in category_ids)}",
                ephemeral=True
            )
        except ValueError:
            await interaction.response.send_message(
                "Invalid category IDs. Please provide numbers only, separated by commas.",
                ephemeral=True
            )
    elif setting.lower() == "enable":
        # Enable the feature
        await update_env_file('REACTION_FORWARD_ENABLED', 'True')
        
        # Update the config
        config.ENABLED = True
        
        await interaction.response.send_message(
            "Reaction forward feature has been enabled.",
            ephemeral=True
        )
    elif setting.lower() == "disable":
        # Disable the feature
        await update_env_file('REACTION_FORWARD_ENABLED', 'False')
        
        # Update the config
        config.ENABLED = False
        
        await interaction.response.send_message(
            "Reaction forward feature has been disabled.",
            ephemeral=True
        )
    elif setting.lower() == "forwarding":
        if not value:
            await interaction.response.send_message(
                "Please provide 'true' or 'false' to enable or disable message forwarding",
                ephemeral=True
            )
            return
            
        if value.lower() in ('true', '1', 't', 'yes', 'y', 'on', 'enable'):
            # Enable forwarding
            await update_env_file('REACTION_FORWARD_ENABLE_FORWARDING', 'True')
            config.ENABLE_FORWARDING = True
            await interaction.response.send_message(
                "Message forwarding has been enabled.",
                ephemeral=True
            )
        elif value.lower() in ('false', '0', 'f', 'no', 'n', 'off', 'disable'):
            # Disable forwarding
            await update_env_file('REACTION_FORWARD_ENABLE_FORWARDING', 'False')
            config.ENABLE_FORWARDING = False
            await interaction.response.send_message(
                "Message forwarding has been disabled.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "Invalid value. Please use 'true' or 'false'.",
                ephemeral=True
            )
    elif setting.lower() == "blacklist":
        if not value:
            await interaction.response.send_message(
                "Please provide channel IDs separated by commas. Example: `123456789,987654321`",
                ephemeral=True
            )
            return
        
        # Validate the channel IDs
        try:
            # Extract IDs from the comma-separated string
            channel_ids = [int(chan_id.strip()) for chan_id in value.split(',') if chan_id.strip()]
            
            # Update the .env file
            await update_env_file('REACTION_FORWARD_BLACKLIST_CHANNEL_IDS', value)
            
            # Update the config
            config.BLACKLIST_CHANNEL_IDS = channel_ids
            
            await interaction.response.send_message(
                f"Updated reaction forward blacklisted channel IDs to: {', '.join(str(chan_id) for chan_id in channel_ids)}",
                ephemeral=True
            )
        except ValueError:
            await interaction.response.send_message(
                "Invalid channel IDs. Please provide numbers only, separated by commas.",
                ephemeral=True
            )
    else:
        await interaction.response.send_message(
            f"Unknown setting: {setting}. Available settings: categories, enable, disable, forwarding, blacklist",
            ephemeral=True
        )

def setup_config_cmd(bot):
    """
    Register the reaction-forward-config slash command.
    
    Args:
        bot: The Discord bot instance
    """
    logger.info("Registering reaction-forward-config command")
    
    # Import the permission decorator
    from utils.permissions import mod_only
    
    @bot.tree.command(
        name="reaction-forward-config",
        description="Configure the reaction forward feature"
    )
    @app_commands.describe(
        setting="The setting to view or modify (categories, enable, disable, forwarding, blacklist)",
        value="The new value for the setting"
    )
    @mod_only()
    async def reaction_forward_config(interaction: discord.Interaction, setting: str = None, value: str = None):
        await handle_reaction_forward_config(interaction, setting, value)
        
    logger.info("Registered reaction-forward-config command") 