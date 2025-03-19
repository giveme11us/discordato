"""
Keyword Filter Configuration Command

Provides a slash command interface for configuring the keyword filter feature.
"""

import discord
from discord import app_commands
import logging
import json
from typing import Dict, List, Optional, Union
from config import keyword_filter_config as config
from config import embed_config

logger = logging.getLogger('discord_bot.modules.mod.keyword_filter.config_cmd')

@app_commands.command(
    name="keyword-filter-quicksetup",
    description="Quick setup for keyword filter with a single command"
)
@app_commands.describe(
    source_channel="The channel or category ID to monitor for keywords",
    notification_channel="The channel ID where notifications will be sent",
    keywords="Comma-separated list of keywords to filter (e.g., 'test,hello,example')"
)
async def keyword_filter_quicksetup(
    interaction: discord.Interaction,
    source_channel: str,
    notification_channel: str,
    keywords: str
):
    """
    Quick setup for the keyword filter with a single command.
    
    Args:
        interaction: The Discord interaction
        source_channel: The channel or category ID to monitor
        notification_channel: The channel ID to send notifications to
        keywords: Comma-separated list of keywords to filter
    """
    # Check permissions - only allow guild admins or users with manage_messages permission
    if not interaction.user.guild_permissions.administrator and not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ You need administrator or manage messages permission to use this command.", ephemeral=True)
        return
    
    try:
        # Parse source channel ID
        try:
            source_id = int(source_channel.strip())
        except ValueError:
            await interaction.response.send_message("❌ Invalid source channel ID. Please provide a valid numeric ID.", ephemeral=True)
            return
        
        # Parse notification channel ID
        try:
            notif_id = int(notification_channel.strip())
        except ValueError:
            await interaction.response.send_message("❌ Invalid notification channel ID. Please provide a valid numeric ID.", ephemeral=True)
            return
        
        # Verify the channels exist
        source_channel_obj = interaction.guild.get_channel(source_id)
        notif_channel_obj = interaction.guild.get_channel(notif_id)
        
        if not source_channel_obj:
            await interaction.response.send_message("❌ Source channel/category not found. Please check the ID.", ephemeral=True)
            return
        
        if not notif_channel_obj:
            await interaction.response.send_message("❌ Notification channel not found. Please check the ID.", ephemeral=True)
            return
        
        # Parse the keywords
        keyword_list = [kw.strip() for kw in keywords.split(',') if kw.strip()]
        if not keyword_list:
            await interaction.response.send_message("❌ No valid keywords provided. Please provide a comma-separated list of keywords.", ephemeral=True)
            return
        
        # Check if it's a category or regular channel
        is_category = isinstance(source_channel_obj, discord.CategoryChannel)
        
        # Here we'll configure the keyword filter
        # 1. Enable the feature
        config.ENABLED = True
        
        # 2. Set notification channel
        config.NOTIFICATION_CHANNEL_ID = notif_id
        config.NOTIFY_FILTERED = True
        
        # 3. Add source channel/category to monitored list
        if is_category:
            config.CATEGORY_IDS.add(source_id)
        else:
            # If it's a regular channel, add its category to the monitored list
            # and add other channels in that category to the blacklist
            if source_channel_obj.category_id:
                config.CATEGORY_IDS.add(source_channel_obj.category_id)
                
                # Add all channels except source_channel_obj to blacklist
                for channel in source_channel_obj.category.channels:
                    if channel.id != source_id:
                        config.BLACKLIST_CHANNEL_IDS.add(channel.id)
        
        # 4. Create a filter for the keywords
        filter_id = f"quicksetup_filter_{interaction.id}"
        config.FILTERS[filter_id] = {
            "enabled": True,
            "patterns": keyword_list,
            "description": f"Quick setup filter created by {interaction.user}",
            "action": "notify",
            "severity": "medium"
        }
        
        # 5. Disable dry run mode
        config.DRY_RUN = False
        
        # Save all configuration changes to persistent storage
        config.save_config()
        
        # Create a response embed
        embed = discord.Embed(
            title="✅ Keyword Filter Quick Setup Complete",
            description="Your keyword filter has been set up successfully!",
            color=discord.Color.green()
        )
        
        # Source channel info
        if is_category:
            embed.add_field(
                name="Monitored Category",
                value=f"{source_channel_obj.name} ({source_id})",
                inline=True
            )
        else:
            embed.add_field(
                name="Monitored Channel",
                value=f"{source_channel_obj.name} ({source_id})",
                inline=True
            )
        
        # Add blacklist info
        embed.add_field(
            name="Blacklisted Channels",
            value="None",
            inline=True
        )
        
        # Notification channel info
        embed.add_field(
            name="Notification Channel",
            value=f"{notification_channel_obj.name} ({notif_id})",
            inline=True
        )
        
        # Keywords info
        keywords_formatted = ", ".join([f"`{kw}`" for kw in keyword_list])
        embed.add_field(
            name="Keywords",
            value=keywords_formatted,
            inline=False
        )
        
        # Apply default styling to the embed
        embed = embed_config.apply_default_styling(embed)
        
        await interaction.response.send_message(embed=embed)
        logger.info(f"Keyword filter quick setup completed by {interaction.user}. Monitoring source {source_id}, notifications to {notif_id}, keywords: {keyword_list}")
        
    except Exception as e:
        logger.error(f"Error during keyword filter quick setup: {str(e)}")
        await interaction.response.send_message(f"❌ An error occurred: {str(e)}", ephemeral=True)

@app_commands.command(
    name="keyword-filter-config",
    description="Configure the keyword filter feature"
)
@app_commands.describe(
    action="The action to perform (view, enable, disable, categories, blacklist, filters, dry_run)",
    filter_id="The filter ID to configure (for filters action)",
    setting="The setting to modify for the selected filter or feature",
    value="The new value for the setting"
)
@app_commands.choices(
    action=[
        app_commands.Choice(name="view", value="view"),
        app_commands.Choice(name="enable", value="enable"),
        app_commands.Choice(name="disable", value="disable"),
        app_commands.Choice(name="categories", value="categories"),
        app_commands.Choice(name="blacklist", value="blacklist"),
        app_commands.Choice(name="notification", value="notification"),
        app_commands.Choice(name="dry_run", value="dry_run"),
        app_commands.Choice(name="filters", value="filters")
    ],
    setting=[
        app_commands.Choice(name="add", value="add"),
        app_commands.Choice(name="remove", value="remove"),
        app_commands.Choice(name="enable", value="enable"),
        app_commands.Choice(name="disable", value="disable"),
        app_commands.Choice(name="description", value="description"),
        app_commands.Choice(name="action", value="action"),
        app_commands.Choice(name="severity", value="severity"),
        app_commands.Choice(name="patterns", value="patterns")
    ]
)
async def keyword_filter_config(
    interaction: discord.Interaction, 
    action: str = "view",
    filter_id: str = None,
    setting: str = None,
    value: str = None
):
    """Configure the keyword filter feature"""
    # Check permissions - only allow guild admins or users with manage_messages permission
    if not interaction.user.guild_permissions.administrator and not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ You need administrator or manage messages permission to use this command.", ephemeral=True)
        return

    if action == "view":
        await show_config(interaction)
    elif action == "enable":
        # Enable the keyword filter feature
        config.ENABLED = True
        config.save_config()
        await interaction.response.send_message("✅ Keyword filter feature enabled.", ephemeral=True)
    elif action == "disable":
        # Disable the keyword filter feature
        config.ENABLED = False
        config.save_config()
        await interaction.response.send_message("✅ Keyword filter feature disabled.", ephemeral=True)
    elif action == "categories":
        # Handle category configuration
        await handle_categories(interaction, setting, value)
    elif action == "blacklist":
        # Handle blacklist configuration
        await handle_blacklist(interaction, setting, value)
    elif action == "notification":
        # Handle notification configuration
        await handle_notification(interaction, setting, value)
    elif action == "dry_run":
        # Handle dry run configuration
        await handle_dry_run(interaction, value)
    elif action == "filters":
        # Handle filter management
        await handle_filters(interaction, filter_id, setting, value)
    else:
        await interaction.response.send_message(f"❌ Unknown action: {action}. Use 'view', 'enable', 'disable', 'categories', 'blacklist', 'notification', 'dry_run', or 'filters'.", ephemeral=True)

async def show_config(interaction):
    """Show the current configuration."""
    # Create an embed with the current configuration
    embed = discord.Embed(
        title="Keyword Filter Configuration",
        description="Current settings for the keyword filter feature.",
        color=discord.Color.blue()
    )
    
    # Add basic configuration fields
    embed.add_field(name="Status", value="Enabled ✅" if config.ENABLED else "Disabled ❌", inline=False)
    
    # Add category information
    category_list = []
    for cat_id in config.CATEGORY_IDS:
        category = interaction.guild.get_channel(cat_id)
        if category:
            category_list.append(f"{category.name} ({cat_id})")
        else:
            category_list.append(f"Unknown ({cat_id})")
    
    if category_list:
        embed.add_field(name="Monitored Categories", value="\n".join(category_list), inline=False)
    
    # Add blacklist information
    blacklist_items = []
    for channel_id in config.BLACKLIST_CHANNEL_IDS:
        channel = interaction.guild.get_channel(channel_id)
        if channel:
            blacklist_items.append(f"{channel.name} ({channel_id})")
        else:
            blacklist_items.append(f"Unknown ({channel_id})")
    
    if blacklist_items:
        embed.add_field(name="Blacklisted Channels", value="\n".join(blacklist_items), inline=False)
    
    # Add notification channel
    if config.NOTIFICATION_CHANNEL_ID:
        channel = interaction.guild.get_channel(config.NOTIFICATION_CHANNEL_ID)
        if channel:
            embed.add_field(name="Notification Channel", value=f"{channel.name} ({config.NOTIFICATION_CHANNEL_ID})", inline=False)
        else:
            embed.add_field(name="Notification Channel", value=f"Unknown ({config.NOTIFICATION_CHANNEL_ID})", inline=False)
    else:
        embed.add_field(name="Notification Channel", value="Not configured", inline=False)
    
    # Add dry run status
    embed.add_field(name="Dry Run Mode", value="Enabled ✅" if config.DRY_RUN else "Disabled ❌", inline=False)
    
    # Apply default styling to the embed
    embed = embed_config.apply_default_styling(embed)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

async def handle_categories(interaction, setting, value):
    """Handle category configuration."""
    if setting == "add":
        # Add a category to the whitelist
        try:
            category = await resolve_category(interaction, value)
            if not category:
                return
            
            # Check if the category is already in the whitelist
            if category.id in config.CATEGORY_IDS:
                await interaction.response.send_message(f"❌ Category {category.name} is already in the whitelist.", ephemeral=True)
                return
            
            # Add the category to the whitelist
            config.CATEGORY_IDS.add(category.id)
            
            # Save the updated configuration
            config.save_config()
            
            await interaction.response.send_message(f"✅ Added category {category.name} to the whitelist.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error adding category: {str(e)}")
            await interaction.response.send_message(f"❌ Error adding category: {str(e)}", ephemeral=True)
    
    elif setting == "remove":
        # Remove a category from the whitelist
        try:
            category = await resolve_category(interaction, value)
            if not category:
                return
            
            # Check if the category is in the whitelist
            if category.id not in config.CATEGORY_IDS:
                await interaction.response.send_message(f"❌ Category {category.name} is not in the whitelist.", ephemeral=True)
                return
            
            # Remove the category from the whitelist
            config.CATEGORY_IDS.remove(category.id)
            
            # Save the updated configuration
            config.save_config()
            
            await interaction.response.send_message(f"✅ Removed category {category.name} from the whitelist.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error removing category: {str(e)}")
            await interaction.response.send_message(f"❌ Error removing category: {str(e)}", ephemeral=True)
    
    elif setting == "list":
        # List whitelisted categories
        category_list = []
        for cat_id in config.CATEGORY_IDS:
            category = interaction.guild.get_channel(cat_id)
            if category:
                category_list.append(f"{category.name} ({cat_id})")
            else:
                category_list.append(f"Unknown ({cat_id})")
        
        if category_list:
            await interaction.response.send_message(f"Whitelisted Categories:\n{chr(10).join(category_list)}", ephemeral=True)
        else:
            await interaction.response.send_message("No categories in the whitelist.", ephemeral=True)
    
    else:
        await interaction.response.send_message(f"❌ Unknown setting: {setting}. Use 'add', 'remove', or 'list'.", ephemeral=True)

async def handle_blacklist(interaction, setting, value):
    """Handle blacklist configuration."""
    if setting == "add":
        # Add a channel to the blacklist
        try:
            channel = await resolve_channel(interaction, value)
            if not channel:
                return
            
            # Check if the channel is already in the blacklist
            if channel.id in config.BLACKLIST_CHANNEL_IDS:
                await interaction.response.send_message(f"❌ Channel {channel.name} is already in the blacklist.", ephemeral=True)
                return
            
            # Add the channel to the blacklist
            config.BLACKLIST_CHANNEL_IDS.add(channel.id)
            
            # Save the updated configuration
            config.save_config()
            
            await interaction.response.send_message(f"✅ Added channel {channel.name} to the blacklist.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error adding channel to blacklist: {str(e)}")
            await interaction.response.send_message(f"❌ Error adding channel to blacklist: {str(e)}", ephemeral=True)
    
    elif setting == "remove":
        # Remove a channel from the blacklist
        try:
            channel = await resolve_channel(interaction, value)
            if not channel:
                return
            
            # Check if the channel is in the blacklist
            if channel.id not in config.BLACKLIST_CHANNEL_IDS:
                await interaction.response.send_message(f"❌ Channel {channel.name} is not in the blacklist.", ephemeral=True)
                return
            
            # Remove the channel from the blacklist
            config.BLACKLIST_CHANNEL_IDS.remove(channel.id)
            
            # Save the updated configuration
            config.save_config()
            
            await interaction.response.send_message(f"✅ Removed channel {channel.name} from the blacklist.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error removing channel from blacklist: {str(e)}")
            await interaction.response.send_message(f"❌ Error removing channel from blacklist: {str(e)}", ephemeral=True)
    
    elif setting == "list":
        # List blacklisted channels
        blacklist = []
        for channel_id in config.BLACKLIST_CHANNEL_IDS:
            channel = interaction.guild.get_channel(channel_id)
            if channel:
                blacklist.append(f"{channel.name} ({channel_id})")
            else:
                blacklist.append(f"Unknown ({channel_id})")
        
        if blacklist:
            await interaction.response.send_message(f"Blacklisted Channels:\n{chr(10).join(blacklist)}", ephemeral=True)
        else:
            await interaction.response.send_message("No channels in the blacklist.", ephemeral=True)
    
    else:
        await interaction.response.send_message(f"❌ Unknown setting: {setting}. Use 'add', 'remove', or 'list'.", ephemeral=True)

async def handle_notification(interaction, setting, value):
    """Handle notification configuration."""
    if setting == "channel":
        if value:
            try:
                # Try to parse channel ID or mention
                channel_id = value.strip()
                if channel_id.startswith('<#') and channel_id.endswith('>'):
                    channel_id = channel_id[2:-1]
                    
                channel_id = int(channel_id)
                channel = interaction.guild.get_channel(channel_id)
                
                if not channel:
                    await interaction.response.send_message(f"❌ Channel with ID {channel_id} not found.", ephemeral=True)
                    return
                    
                if not isinstance(channel, discord.TextChannel):
                    await interaction.response.send_message(f"❌ {channel.name} is not a text channel.", ephemeral=True)
                    return
                
                # Set the notification channel
                config.NOTIFICATION_CHANNEL_ID = channel_id
                
                # Save the updated configuration
                config.save_config()
                
                await interaction.response.send_message(f"✅ Set notification channel to {channel.mention}.", ephemeral=True)
                
            except ValueError:
                await interaction.response.send_message("❌ Invalid channel ID or mention. Please provide a valid channel ID or mention.", ephemeral=True)
                
        else:
            # Show current notification channel
            if config.NOTIFICATION_CHANNEL_ID:
                channel = interaction.guild.get_channel(config.NOTIFICATION_CHANNEL_ID)
                if channel:
                    await interaction.response.send_message(f"Current notification channel: {channel.mention} ({config.NOTIFICATION_CHANNEL_ID})", ephemeral=True)
                else:
                    await interaction.response.send_message(f"Current notification channel ID: {config.NOTIFICATION_CHANNEL_ID} (channel not found)", ephemeral=True)
            else:
                await interaction.response.send_message("No notification channel set.", ephemeral=True)
    
    elif setting == "enable":
        # Enable notifications
        config.NOTIFY_FILTERED = True
        config.save_config()
        await interaction.response.send_message("✅ Keyword filter notifications enabled.", ephemeral=True)
    
    elif setting == "disable":
        # Disable notifications
        config.NOTIFY_FILTERED = False
        config.save_config()
        await interaction.response.send_message("✅ Keyword filter notifications disabled.", ephemeral=True)
    
    else:
        # Show notification settings
        notification_status = "Enabled" if config.NOTIFY_FILTERED else "Disabled"
        
        if config.NOTIFICATION_CHANNEL_ID:
            channel = interaction.guild.get_channel(config.NOTIFICATION_CHANNEL_ID)
            channel_info = f"{channel.mention} ({config.NOTIFICATION_CHANNEL_ID})" if channel else f"{config.NOTIFICATION_CHANNEL_ID} (channel not found)"
        else:
            channel_info = "Not set"
            
        await interaction.response.send_message(
            f"**Notification Settings**\n"
            f"Status: {notification_status}\n"
            f"Channel: {channel_info}\n\n"
            f"Use `/keyword-filter-config notification enable` or `disable` to toggle notifications.\n"
            f"Use `/keyword-filter-config notification channel #channel` to set the notification channel.",
            ephemeral=True
        )

async def handle_dry_run(interaction, value):
    """Handle dry run configuration."""
    if value and value.lower() in ('true', 'yes', '1', 'on', 'enable'):
        # Enable dry run mode
        config.DRY_RUN = True
        config.save_config()
        await interaction.response.send_message("✅ Dry run mode enabled. Messages will be logged but not deleted.", ephemeral=True)
    
    elif value and value.lower() in ('false', 'no', '0', 'off', 'disable'):
        # Disable dry run mode
        config.DRY_RUN = False
        config.save_config()
        await interaction.response.send_message("✅ Dry run mode disabled. Messages will be processed according to filter actions.", ephemeral=True)
    
    else:
        # Show current dry run status
        status = "Enabled" if config.DRY_RUN else "Disabled"
        await interaction.response.send_message(
            f"**Dry Run Mode**: {status}\n\n"
            f"When enabled, messages will be logged and notifications sent, but no messages will be deleted.\n"
            f"Use `/keyword-filter-config dry_run true` or `false` to toggle dry run mode.",
            ephemeral=True
        )

async def handle_filters(interaction, filter_id, setting, value):
    """Handle filter configuration."""
    # If no filter ID is provided, show a list of available filters
    if not filter_id:
        await list_filters(interaction)
        return
    
    # If no setting is provided, show details for the specified filter
    if not setting:
        await view_filter(interaction, filter_id)
        return
    
    # Handle add action - create a new filter
    if filter_id == "add" and setting and value:
        # Create a new filter with the given name and description
        new_id = setting.lower().replace(' ', '_')
        
        # Check if filter already exists
        if new_id in config.FILTERS:
            await interaction.response.send_message(f"❌ Filter with ID '{new_id}' already exists. Use a different name or edit the existing filter.", ephemeral=True)
            return
        
        # Create the new filter
        config.FILTERS[new_id] = {
            "enabled": True,
            "patterns": [],
            "description": value,
            "action": "notify",
            "severity": "medium"
        }
        
        config.save_config()
        
        await interaction.response.send_message(f"✅ Added new filter '{new_id}' with description '{value}'.", ephemeral=True)
        return
    
    # Check if the filter exists
    if filter_id not in config.FILTERS:
        await interaction.response.send_message(f"❌ Filter with ID '{filter_id}' not found. Use `/keyword-filter-config filters` to see available filters.", ephemeral=True)
        return
    
    # Handle remove action - delete a filter
    if setting == "remove":
        filter_desc = config.FILTERS[filter_id].get('description', 'No description')
        del config.FILTERS[filter_id]
        
        config.save_config()
        
        await interaction.response.send_message(f"✅ Removed filter '{filter_id}' ({filter_desc}).", ephemeral=True)
        return
    
    # Handle enable action - enable a filter
    if setting == "enable":
        # Enable the filter
        config.FILTERS[filter_id]['enabled'] = True
        
        config.save_config()
        
        await interaction.response.send_message(f"✅ Enabled filter '{filter_id}'.", ephemeral=True)
        return
    
    # Handle disable action - disable a filter
    if setting == "disable":
        # Disable the filter
        config.FILTERS[filter_id]['enabled'] = False
        
        config.save_config()
        
        await interaction.response.send_message(f"✅ Disabled filter '{filter_id}'.", ephemeral=True)
        return
    
    # Handle description action - update filter description
    if setting == "description" and value:
        old_desc = config.FILTERS[filter_id].get('description', 'No description')
        config.FILTERS[filter_id]['description'] = value
        
        config.save_config()
        
        await interaction.response.send_message(f"✅ Updated filter description from '{old_desc}' to '{value}'.", ephemeral=True)
        return
    
    # Handle action action - update filter action
    if setting == "action" and value:
        if value.lower() not in ('log', 'notify', 'delete'):
            await interaction.response.send_message(f"❌ Invalid action: {value}. Valid actions are: log, notify, delete.", ephemeral=True)
            return
        
        old_action = config.FILTERS[filter_id].get('action', 'log')
        config.FILTERS[filter_id]['action'] = value.lower()
        
        config.save_config()
        
        await interaction.response.send_message(f"✅ Updated filter action from '{old_action}' to '{value.lower()}'.", ephemeral=True)
        return
    
    # Handle severity action - update filter severity
    if setting == "severity" and value:
        if value.lower() not in ('low', 'medium', 'high'):
            await interaction.response.send_message(f"❌ Invalid severity: {value}. Valid severities are: low, medium, high.", ephemeral=True)
            return
        
        old_severity = config.FILTERS[filter_id].get('severity', 'medium')
        config.FILTERS[filter_id]['severity'] = value.lower()
        
        config.save_config()
        
        await interaction.response.send_message(f"✅ Updated filter severity from '{old_severity}' to '{value.lower()}'.", ephemeral=True)
        return
    
    # Handle patterns action - update filter patterns
    if setting == "patterns":
        await handle_patterns(interaction, filter_id, value)
        return
    
    # If we get here, we didn't handle the command
    await interaction.response.send_message(
        f"❌ Unknown setting: {setting}. Valid settings are: remove, enable, disable, description, action, severity, patterns.", 
        ephemeral=True
    )

async def handle_patterns(interaction, filter_id, value_str):
    """Handle pattern management for a filter."""
    if not value_str or ":" not in value_str:
        await interaction.response.send_message(
            "❌ Please specify a pattern management action using the format: `action:value`. "
            "Valid actions are: add, remove, set, list.", 
            ephemeral=True
        )
        return
    
    action, value = value_str.split(":", 1)
    action = action.lower().strip()
    value = value.strip()
    
    # Handle pattern listing
    if action == "list":
        patterns = config.FILTERS[filter_id].get('patterns', [])
        if not patterns:
            await interaction.response.send_message(f"❌ No patterns configured for filter '{filter_id}'.", ephemeral=True)
            return
        
        # Create a formatted list of patterns
        pattern_list = "\n".join([f"{i+1}. `{p}`" for i, p in enumerate(patterns)])
        
        await interaction.response.send_message(f"**Patterns for filter '{filter_id}'**:\n{pattern_list}", ephemeral=True)
        return
    
    # Handle adding a pattern
    if action == "add":
        if not value:
            await interaction.response.send_message("❌ Please provide a pattern to add.", ephemeral=True)
            return
        
        # Ensure the patterns list exists
        if 'patterns' not in config.FILTERS[filter_id]:
            config.FILTERS[filter_id]['patterns'] = []
        
        # Add the pattern if it doesn't already exist
        if value not in config.FILTERS[filter_id]['patterns']:
            config.FILTERS[filter_id]['patterns'].append(value)
            config.save_config()
            await interaction.response.send_message(f"✅ Added pattern `{value}` to filter '{filter_id}'.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Pattern `{value}` already exists in filter '{filter_id}'.", ephemeral=True)
        return
    
    # Handle removing a pattern
    if action == "remove":
        if not value:
            await interaction.response.send_message("❌ Please provide a pattern or pattern index to remove.", ephemeral=True)
            return
        
        patterns = config.FILTERS[filter_id].get('patterns', [])
        
        # Try to remove by index
        try:
            index = int(value) - 1  # Convert to 0-indexed
            if 0 <= index < len(patterns):
                removed = patterns.pop(index)
                config.save_config()
                await interaction.response.send_message(f"✅ Removed pattern `{removed}` from filter '{filter_id}'.", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ Invalid pattern index. Please use an index between 1 and {len(patterns)}.", ephemeral=True)
        except ValueError:
            # Not an index, try to remove by value
            if value in patterns:
                patterns.remove(value)
                config.save_config()
                await interaction.response.send_message(f"✅ Removed pattern `{value}` from filter '{filter_id}'.", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ Pattern `{value}` not found in filter '{filter_id}'.", ephemeral=True)
        return
    
    # Handle setting all patterns at once
    if action == "set":
        # Split the value by commas, trim whitespace, and filter out empty strings
        new_patterns = [p.strip() for p in value.split(',') if p.strip()]
        
        if not new_patterns:
            await interaction.response.send_message("❌ Please provide at least one pattern.", ephemeral=True)
            return
        
        # Update the patterns
        config.FILTERS[filter_id]['patterns'] = new_patterns
        config.save_config()
        
        patterns_str = "\n".join([f"{i+1}. `{p}`" for i, p in enumerate(new_patterns)])
        await interaction.response.send_message(f"✅ Set patterns for filter '{filter_id}':\n{patterns_str}", ephemeral=True)
        return
    
    # If we get here, an invalid action was specified
    await interaction.response.send_message(
        f"❌ Invalid pattern action: {action}. Valid actions are: add, remove, set, list.", 
        ephemeral=True
    )

async def list_filters(interaction):
    """Show a list of configured filters."""
    if not config.FILTERS:
        await interaction.response.send_message("No filters configured. Use `/keyword-filter-config filters add filter_name \"Description\"` to add a filter.", ephemeral=True)
        return
    
    # Create an embed to display the filters
    embed = discord.Embed(
        title="Keyword Filter Rules",
        description="List of all configured filter rules.",
        color=discord.Color.blue()
    )
    
    for filter_id, filter_data in config.FILTERS.items():
        if filter_data.get('enabled', True):
            status = "✅ Enabled"
        else:
            status = "❌ Disabled"
        
        description = filter_data.get('description', 'No description')
        severity = filter_data.get('severity', 'medium').capitalize()
        action = filter_data.get('action', 'alert').capitalize()
        
        # Count patterns
        pattern_count = len(filter_data.get('patterns', []))
        
        value = f"{description}\n**Status:** {status}\n**Severity:** {severity}\n**Action:** {action}\n**Patterns:** {pattern_count}"
        embed.add_field(name=f"Rule: {filter_id}", value=value, inline=False)
    
    if not config.FILTERS:
        embed.description = "No filter rules configured yet."
    
    # Apply default styling to the embed
    embed = embed_config.apply_default_styling(embed)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

async def view_filter(interaction, filter_id):
    """Show details for a specific filter."""
    # Check if the filter exists
    if filter_id not in config.FILTERS:
        await interaction.response.send_message(f"❌ Filter with ID '{filter_id}' not found. Use `/keyword-filter-config filters` to see available filters.", ephemeral=True)
        return
    
    # Get the filter configuration
    filter_data = config.FILTERS[filter_id]
    enabled = filter_data.get('enabled', False)
    description = filter_data.get('description', 'No description')
    action = filter_data.get('action', 'log')
    severity = filter_data.get('severity', 'medium')
    patterns = filter_data.get('patterns', [])
    
    # Create an embed to display the filter details
    embed = discord.Embed(
        title=f"Filter Rule: {filter_id}",
        description=filter_data.get('description', 'No description'),
        color=discord.Color.blue()
    )
    
    # Status
    if filter_data.get('enabled', True):
        status = "✅ Enabled"
    else:
        status = "❌ Disabled"
    embed.add_field(name="Status", value=status, inline=True)
    
    # Severity
    severity = filter_data.get('severity', 'medium').capitalize()
    embed.add_field(name="Severity", value=severity, inline=True)
    
    # Action
    action = filter_data.get('action', 'alert').capitalize()
    embed.add_field(name="Action", value=action, inline=True)
    
    # Pattern count
    embed.add_field(name="Patterns", value=str(len(patterns)), inline=True)
    
    # List patterns
    if patterns:
        pattern_list = "\n".join([f"• `{pattern}`" for pattern in patterns])
        embed.add_field(name="Pattern List", value=pattern_list, inline=False)
    else:
        embed.add_field(name="Pattern List", value="No patterns configured", inline=False)
    
    # Apply default styling to the embed
    embed = embed_config.apply_default_styling(embed)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

async def resolve_category(interaction, value):
    """Resolve a category from a mention, ID, or name."""
    if not value:
        await interaction.response.send_message("❌ Please provide a category ID, name, or mention.", ephemeral=True)
        return None
    
    # Try to resolve as ID
    try:
        category_id = int(value.strip())
        category = interaction.guild.get_channel(category_id)
        if category and isinstance(category, discord.CategoryChannel):
            return category
    except ValueError:
        pass
    
    # Try to resolve as name
    for category in interaction.guild.categories:
        if category.name.lower() == value.lower():
            return category
    
    await interaction.response.send_message(f"❌ Could not find category: {value}", ephemeral=True)
    return None

async def resolve_channel(interaction, value):
    """Resolve a channel from a mention, ID, or name."""
    if not value:
        await interaction.response.send_message("❌ Please provide a channel ID, name, or mention.", ephemeral=True)
        return None
    
    # Try to resolve as mention
    if value.startswith("<#") and value.endswith(">"):
        channel_id = int(value[2:-1])
        channel = interaction.guild.get_channel(channel_id)
        if channel:
            return channel
    
    # Try to resolve as ID
    try:
        channel_id = int(value.strip())
        channel = interaction.guild.get_channel(channel_id)
        if channel:
            return channel
    except ValueError:
        pass
    
    # Try to resolve as name
    for channel in interaction.guild.channels:
        if channel.name.lower() == value.lower():
            return channel
    
    await interaction.response.send_message(f"❌ Could not find channel: {value}", ephemeral=True)
    return None 