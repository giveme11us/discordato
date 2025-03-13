"""
Configuration command for the link reaction feature.
"""

import logging
import discord
from discord.ext import commands
from discord import app_commands
from config import link_reaction_config as config
from config import pinger_config
from utils.config_utils import update_env_file, parse_id_list

logger = logging.getLogger('discord_bot.modules.mod.link_reaction.config_cmd')

@app_commands.command(name="link-reaction-config", description="Configure the link reaction feature")
@app_commands.describe(
    setting="The setting to configure (enabled, categories, blacklist)",
    value="The new value for the setting"
)
@app_commands.choices(setting=[
    app_commands.Choice(name="enabled", value="enabled"),
    app_commands.Choice(name="categories", value="categories"),
    app_commands.Choice(name="blacklist", value="blacklist"),
])
async def link_reaction_config(interaction: discord.Interaction, setting: str = None, value: str = None):
    """
    Command to configure the link reaction feature.
    
    Args:
        interaction: The Discord interaction
        setting: The setting to configure
        value: The new value for the setting
    """
    # Check if the user has a whitelisted role
    if not config.WHITELIST_ROLE_IDS:
        await interaction.response.send_message("No roles are whitelisted to use this command.", ephemeral=True)
        return
    
    # Convert user's roles to set of IDs for quick lookup
    user_role_ids = {role.id for role in interaction.user.roles}
    
    # Check if any of the user's roles is in the whitelist
    has_whitelisted_role = any(role_id in user_role_ids for role_id in config.WHITELIST_ROLE_IDS)
    
    if not has_whitelisted_role:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return
    
    # If no setting is provided, show the current configuration
    if not setting:
        embed = discord.Embed(
            title="Link Reaction Configuration",
            description="Current settings for the link reaction feature",
            color=discord.Color.blue()
        )
        
        # Add fields for each setting
        embed.add_field(
            name="Enabled",
            value=f"`{config.ENABLED}`",
            inline=False
        )
        
        # Format the category IDs
        category_ids_str = ", ".join(f"<#{cat_id}>" for cat_id in config.CATEGORY_IDS) if config.CATEGORY_IDS else "None"
        embed.add_field(
            name="Whitelisted Categories",
            value=category_ids_str or "None",
            inline=False
        )
        
        # Format the blacklisted channel IDs
        blacklist_str = ", ".join(f"<#{ch_id}>" for ch_id in config.BLACKLIST_CHANNEL_IDS) if config.BLACKLIST_CHANNEL_IDS else "None"
        embed.add_field(
            name="Blacklisted Channels",
            value=blacklist_str or "None",
            inline=False
        )
        
        # Add instructions for updating settings
        embed.add_field(
            name="How to Update",
            value="Use `/link-reaction-config setting:value` to update a setting.\n"
                  "Examples:\n"
                  "- `/link-reaction-config setting:enabled value:true`\n"
                  "- `/link-reaction-config setting:categories value:123456789,987654321`\n"
                  "- `/link-reaction-config setting:blacklist value:123456789,987654321`",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Handle updating settings
    if setting == "enabled":
        if not value:
            await interaction.response.send_message(f"Current value for 'enabled' is: `{config.ENABLED}`", ephemeral=True)
            return
        
        # Convert value to boolean
        if value.lower() in ("true", "yes", "1", "on"):
            new_value = True
        elif value.lower() in ("false", "no", "0", "off"):
            new_value = False
        else:
            await interaction.response.send_message(f"Invalid value for 'enabled'. Use 'true' or 'false'.", ephemeral=True)
            return
        
        # Update the .env file
        update_env_file("LINK_REACTION_ENABLED", str(new_value))
        
        # Update the config in memory
        config.ENABLED = new_value
        
        await interaction.response.send_message(f"Link reaction feature is now {'enabled' if new_value else 'disabled'}.", ephemeral=True)
        logger.info(f"User {interaction.user} {'enabled' if new_value else 'disabled'} the link reaction feature")
    
    elif setting == "categories":
        if not value:
            # Format the current categories
            categories_str = ", ".join(f"<#{cat_id}>" for cat_id in config.CATEGORY_IDS) if config.CATEGORY_IDS else "None"
            await interaction.response.send_message(f"Current whitelisted categories: {categories_str}", ephemeral=True)
            return
        
        # Parse the new category IDs
        try:
            new_categories = parse_id_list(value)
            
            # Update the .env file
            update_env_file("LINK_REACTION_CATEGORY_IDS", ",".join(map(str, new_categories)))
            
            # Update the config in memory
            config.CATEGORY_IDS = set(new_categories)
            
            # Format the new categories for display
            categories_str = ", ".join(f"<#{cat_id}>" for cat_id in new_categories) if new_categories else "None"
            await interaction.response.send_message(f"Updated whitelisted categories to: {categories_str}", ephemeral=True)
            logger.info(f"User {interaction.user} updated link reaction categories to {new_categories}")
        except ValueError as e:
            await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)
    
    elif setting == "blacklist":
        if not value:
            # Format the current blacklist
            blacklist_str = ", ".join(f"<#{ch_id}>" for ch_id in config.BLACKLIST_CHANNEL_IDS) if config.BLACKLIST_CHANNEL_IDS else "None"
            await interaction.response.send_message(f"Current blacklisted channels: {blacklist_str}", ephemeral=True)
            return
        
        # Parse the new blacklisted channel IDs
        try:
            new_blacklist = parse_id_list(value)
            
            # Update the .env file
            update_env_file("LINK_REACTION_BLACKLIST_CHANNEL_IDS", ",".join(map(str, new_blacklist)))
            
            # Update the config in memory
            config.BLACKLIST_CHANNEL_IDS = set(new_blacklist)
            
            # Format the new blacklist for display
            blacklist_str = ", ".join(f"<#{ch_id}>" for ch_id in new_blacklist) if new_blacklist else "None"
            await interaction.response.send_message(f"Updated blacklisted channels to: {blacklist_str}", ephemeral=True)
            logger.info(f"User {interaction.user} updated link reaction blacklist to {new_blacklist}")
        except ValueError as e:
            await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)
    
    else:
        await interaction.response.send_message(f"Unknown setting: {setting}. Valid settings are: enabled, categories, blacklist", ephemeral=True) 