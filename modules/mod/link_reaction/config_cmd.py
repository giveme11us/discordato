"""
Link Reaction Configuration Command

Provides a slash command interface for configuring the link reaction feature
and managing store configurations.
"""

import discord
from discord import app_commands
import logging
import os
from config import link_reaction_config as config
from modules.mod.link_reaction.store_manager import store_manager
from config import embed_config

logger = logging.getLogger('discord_bot.modules.mod.link_reaction.config_cmd')

@app_commands.command(
    name="link-reaction-config",
    description="Configure the link reaction feature and manage store settings"
)
@app_commands.describe(
    action="The action to perform (view, enable, disable, categories, blacklist, stores)",
    store_id="The store ID to configure (for stores action)",
    setting="The setting to modify for the selected store or feature",
    value="The new value for the setting"
)
@app_commands.choices(
    action=[
        app_commands.Choice(name="view", value="view"),
        app_commands.Choice(name="enable", value="enable"),
        app_commands.Choice(name="disable", value="disable"),
        app_commands.Choice(name="categories", value="categories"),
        app_commands.Choice(name="blacklist", value="blacklist"),
        app_commands.Choice(name="stores", value="stores")
    ],
    setting=[
        app_commands.Choice(name="add", value="add"),
        app_commands.Choice(name="remove", value="remove"),
        app_commands.Choice(name="enable", value="enable"),
        app_commands.Choice(name="disable", value="disable"),
        app_commands.Choice(name="name", value="name"),
        app_commands.Choice(name="file_path", value="file_path"),
        app_commands.Choice(name="detection_type", value="detection_type"),
        app_commands.Choice(name="detection_value", value="detection_value"),
        app_commands.Choice(name="extraction", value="extraction")
    ]
)
async def link_reaction_config(
    interaction: discord.Interaction, 
    action: str = "view",
    store_id: str = None,
    setting: str = None,
    value: str = None
):
    """Configure the link reaction feature and manage store settings"""
    # Check permissions - only allow guild admins or users with manage_messages permission
    if not interaction.user.guild_permissions.administrator and not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ You need administrator or manage messages permission to use this command.", ephemeral=True)
        return

    if action == "view":
        await show_config(interaction)
    elif action == "enable":
        # Enable the link reaction feature
        config.ENABLED = True
        await interaction.response.send_message("✅ Link reaction feature enabled.")
    elif action == "disable":
        # Disable the link reaction feature
        config.ENABLED = False
        await interaction.response.send_message("✅ Link reaction feature disabled.")
    elif action == "categories":
        # Handle category configuration
        await handle_categories(interaction, setting, value)
    elif action == "blacklist":
        # Handle blacklist configuration
        await handle_blacklist(interaction, setting, value)
    elif action == "stores":
        # Handle store management
        await handle_stores(interaction, store_id, setting, value)
    else:
        await interaction.response.send_message(f"❌ Unknown action: {action}. Use 'view', 'enable', 'disable', 'categories', 'blacklist', or 'stores'.", ephemeral=True)

async def show_config(interaction):
    """Show the current configuration."""
    # Create an embed with the current configuration
    embed = discord.Embed(
        title="Link Reaction Configuration",
        description="Current settings for the link reaction feature.",
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
    
    # Add link emoji
    embed.add_field(name="Link Emoji", value=config.LINK_EMOJI, inline=False)
    
    # Add whitelist roles
    role_list = []
    for role_id in config.WHITELIST_ROLE_IDS:
        role = interaction.guild.get_role(role_id)
        if role:
            role_list.append(f"{role.name} ({role_id})")
        else:
            role_list.append(f"Unknown ({role_id})")
    
    if role_list:
        embed.add_field(name="Whitelisted Roles", value="\n".join(role_list), inline=False)
    else:
        embed.add_field(name="Whitelisted Roles", value="None (all users can use the feature)", inline=False)
    
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
            config.CATEGORY_IDS.append(category.id)
            
            # Save the updated configuration
            # TODO: Save to .env file or database
            
            await interaction.response.send_message(f"✅ Added category {category.name} to the whitelist.")
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
            # TODO: Save to .env file or database
            
            await interaction.response.send_message(f"✅ Removed category {category.name} from the whitelist.")
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
            await interaction.response.send_message(f"Whitelisted Categories:\n{chr(10).join(category_list)}")
        else:
            await interaction.response.send_message("No categories in the whitelist.")
    
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
            config.BLACKLIST_CHANNEL_IDS.append(channel.id)
            
            # Save the updated configuration
            # TODO: Save to .env file or database
            
            await interaction.response.send_message(f"✅ Added channel {channel.name} to the blacklist.")
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
            # TODO: Save to .env file or database
            
            await interaction.response.send_message(f"✅ Removed channel {channel.name} from the blacklist.")
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
            await interaction.response.send_message(f"Blacklisted Channels:\n{chr(10).join(blacklist)}")
        else:
            await interaction.response.send_message("No channels in the blacklist.")
    
    else:
        await interaction.response.send_message(f"❌ Unknown setting: {setting}. Use 'add', 'remove', or 'list'.", ephemeral=True)

async def handle_stores(interaction, store_id, setting, value):
    """Handle store configuration."""
    if not store_id and setting != "list":
        # List all stores if no store ID is provided
        await list_stores(interaction)
        return
    
    if setting == "list":
        # List all stores
        await list_stores(interaction)
        return
    
    if setting == "view" and store_id:
        # View a specific store configuration
        await view_store(interaction, store_id)
        return
    
    if setting == "add":
        # Add a new store
        if not value:
            await interaction.response.send_message("❌ Please provide a name for the new store.", ephemeral=True)
            return
        
        # Check if store already exists
        if store_manager.get_store(store_id):
            await interaction.response.send_message(f"❌ Store with ID '{store_id}' already exists.", ephemeral=True)
            return
        
        # Add new store with default settings
        success = store_manager.add_store(
            store_id=store_id,
            name=value,
            file_path=f"data/{store_id}_drop_urls.txt",
            detection_type="author_name",
            detection_value=value,
            extraction_primary="url",
            extraction_pattern=r'\/[^\/]+\/([^\/]+)$',
            description=f"Extract product IDs from {value} embeds"
        )
        
        if success:
            await interaction.response.send_message(f"✅ Added new store '{value}' with ID '{store_id}'.")
        else:
            await interaction.response.send_message(f"❌ Failed to add new store.", ephemeral=True)
    
    elif setting == "remove":
        # Remove a store
        store = store_manager.get_store(store_id)
        if not store:
            await interaction.response.send_message(f"❌ Store with ID '{store_id}' does not exist.", ephemeral=True)
            return
        
        success = store_manager.remove_store(store_id)
        if success:
            await interaction.response.send_message(f"✅ Removed store '{store['name']}' with ID '{store_id}'.")
        else:
            await interaction.response.send_message(f"❌ Failed to remove store.", ephemeral=True)
    
    elif setting == "enable":
        # Enable a store
        store = store_manager.get_store(store_id)
        if not store:
            await interaction.response.send_message(f"❌ Store with ID '{store_id}' does not exist.", ephemeral=True)
            return
        
        success = store_manager.update_store(store_id, enabled=True)
        if success:
            await interaction.response.send_message(f"✅ Enabled store '{store['name']}' with ID '{store_id}'.")
        else:
            await interaction.response.send_message(f"❌ Failed to enable store.", ephemeral=True)
    
    elif setting == "disable":
        # Disable a store
        store = store_manager.get_store(store_id)
        if not store:
            await interaction.response.send_message(f"❌ Store with ID '{store_id}' does not exist.", ephemeral=True)
            return
        
        success = store_manager.update_store(store_id, enabled=False)
        if success:
            await interaction.response.send_message(f"✅ Disabled store '{store['name']}' with ID '{store_id}'.")
        else:
            await interaction.response.send_message(f"❌ Failed to disable store.", ephemeral=True)
    
    elif setting == "name":
        # Update store name
        store = store_manager.get_store(store_id)
        if not store:
            await interaction.response.send_message(f"❌ Store with ID '{store_id}' does not exist.", ephemeral=True)
            return
        
        if not value:
            await interaction.response.send_message("❌ Please provide a new name for the store.", ephemeral=True)
            return
        
        success = store_manager.update_store(store_id, name=value)
        if success:
            await interaction.response.send_message(f"✅ Updated store name from '{store['name']}' to '{value}'.")
        else:
            await interaction.response.send_message(f"❌ Failed to update store name.", ephemeral=True)
    
    elif setting == "file_path":
        # Update store file path
        store = store_manager.get_store(store_id)
        if not store:
            await interaction.response.send_message(f"❌ Store with ID '{store_id}' does not exist.", ephemeral=True)
            return
        
        if not value:
            await interaction.response.send_message("❌ Please provide a file path for the store.", ephemeral=True)
            return
        
        success = store_manager.update_store(store_id, file_path=value)
        if success:
            await interaction.response.send_message(f"✅ Updated file path for store '{store['name']}' to '{value}'.")
        else:
            await interaction.response.send_message(f"❌ Failed to update file path.", ephemeral=True)
    
    elif setting == "detection_type":
        # Update detection type
        store = store_manager.get_store(store_id)
        if not store:
            await interaction.response.send_message(f"❌ Store with ID '{store_id}' does not exist.", ephemeral=True)
            return
        
        if not value or value not in ["author_name", "title_contains", "url_contains"]:
            await interaction.response.send_message("❌ Please provide a valid detection type: author_name, title_contains, or url_contains.", ephemeral=True)
            return
        
        success = store_manager.update_store(store_id, detection_type=value)
        if success:
            await interaction.response.send_message(f"✅ Updated detection type for store '{store['name']}' to '{value}'.")
        else:
            await interaction.response.send_message(f"❌ Failed to update detection type.", ephemeral=True)
    
    elif setting == "detection_value":
        # Update detection value
        store = store_manager.get_store(store_id)
        if not store:
            await interaction.response.send_message(f"❌ Store with ID '{store_id}' does not exist.", ephemeral=True)
            return
        
        if not value:
            await interaction.response.send_message("❌ Please provide a detection value for the store.", ephemeral=True)
            return
        
        success = store_manager.update_store(store_id, detection_value=value)
        if success:
            await interaction.response.send_message(f"✅ Updated detection value for store '{store['name']}' to '{value}'.")
        else:
            await interaction.response.send_message(f"❌ Failed to update detection value.", ephemeral=True)
    
    else:
        await interaction.response.send_message(f"❌ Unknown setting: {setting}. Use 'add', 'remove', 'enable', 'disable', 'name', 'file_path', 'detection_type', or 'detection_value'.", ephemeral=True)

async def list_stores(interaction):
    """List all stores."""
    all_stores = store_manager.get_all_stores()
    
    if not all_stores:
        await interaction.response.send_message("No stores configured.")
        return
    
    # Create an embed with the list of stores
    embed = discord.Embed(
        title="Link Reaction Stores",
        description="List of configured stores for link detection and info extraction.",
        color=discord.Color.blue()
    )
    
    for store_id, store_data in config.STORES.items():
        if store_data.get('enabled', True):
            status = "✅ Enabled"
        else:
            status = "❌ Disabled"
        
        store_name = store_data.get('name', 'Unnamed Store')
        detection_type = store_data.get('detection_type', 'domain')
        detection_value = store_data.get('detection_value', '')
        
        value = f"**Status:** {status}\n**Detection:** {detection_type}={detection_value}"
        embed.add_field(name=f"Store: {store_name} [{store_id}]", value=value, inline=False)
    
    if not config.STORES:
        embed.description = "No stores configured yet."
    
    # Apply default styling to the embed
    embed = embed_config.apply_default_styling(embed)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

async def view_store(interaction, store_id):
    """View a specific store configuration."""
    store = store_manager.get_store(store_id)
    
    if not store:
        await interaction.response.send_message(f"❌ Store with ID '{store_id}' does not exist.", ephemeral=True)
        return
    
    # Create an embed with the store details
    embed = discord.Embed(
        title=f"Store Details: {store['name']}",
        description=f"Configuration for store ID: {store_id}",
        color=discord.Color.blue()
    )
    
    # Status
    if store.get("enabled", True):
        status = "✅ Enabled"
    else:
        status = "❌ Disabled"
    embed.add_field(name="Status", value=status, inline=True)
    
    # Detection method
    detection_type = store.get("detection_type", "domain")
    detection_value = store.get("detection_value", "")
    embed.add_field(name="Detection Type", value=detection_type, inline=True)
    embed.add_field(name="Detection Value", value=detection_value, inline=True)
    
    # Extraction 
    extraction = store.get("extraction", {})
    extraction_text = ""
    
    if extraction:
        for key, pattern in extraction.items():
            extraction_text += f"**{key}**: `{pattern}`\n"
    else:
        extraction_text = "No extraction patterns configured"
    
    embed.add_field(name="Extraction Patterns", value=extraction_text, inline=False)
    
    # File path
    file_path = store.get("file_path", "")
    if file_path:
        embed.add_field(name="Storage File", value=f"`{file_path}`", inline=False)
    else:
        embed.add_field(name="Storage File", value="Not configured", inline=False)
    
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