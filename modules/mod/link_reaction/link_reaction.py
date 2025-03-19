"""
Link Reaction Feature

This module monitors messages in specified categories
and adds a link emoji reaction to them for supported stores.
"""

import logging
import discord
import os
import re
from config import link_reaction_config as config
from config import pinger_config
from config import reaction_forward_config as forward_config
from modules.mod.link_reaction.store_manager import store_manager

# Keep asyncio import as it's used for the delay when adding reactions
import asyncio

logger = logging.getLogger('discord_bot.modules.mod.link_reaction')

async def process_message(message):
    """
    Process a message to check for store links.
    
    Args:
        message: The Discord message to process
    """
    # Get settings directly from settings manager
    enabled = config.settings_manager.get("ENABLED", False)
    category_ids = config.settings_manager.get("CATEGORY_IDS", [])
    blacklist_channel_ids = config.settings_manager.get("BLACKLIST_CHANNEL_IDS", [])
    whitelist_role_ids = config.settings_manager.get("WHITELIST_ROLE_IDS", [])
    stores = config.settings_manager.get("STORES", {})
    
    # Skip if link reaction is disabled
    if not enabled:
        return
    
    # Log the configuration being used
    logger.debug(f"Link reaction processing message with config - enabled: {enabled}, category IDs: {category_ids}")
    if isinstance(stores, dict):
        logger.debug(f"Stores configured: {list(stores.keys()) if stores else 'None'}")
    else:
        logger.debug(f"Stores configured (legacy format): {len(stores) if stores else 'None'}")
    
    # Skip bot messages (except for webhooks and application messages)
    if message.author.bot and not (message.webhook_id or message.application_id):
        logger.debug(f"Skipping message from bot (non-webhook): {message.author}")
        return
    
    # Skip if not in a guild
    if not message.guild:
        logger.debug("Message not in a guild, skipping")
        return
    
    # Skip if the channel is in the blacklist
    if message.channel.id in blacklist_channel_ids:
        logger.debug(f"Skipping message in blacklisted channel: {message.channel.name}")
        return
    
    # Skip if the channel is the notification channel
    notification_channel_id = pinger_config.settings_manager.get("NOTIFICATION_CHANNEL_ID")
    if message.channel.id == notification_channel_id:
        logger.debug(f"Skipping message in notification channel")
        return
    
    # Check if channel ID matches any store's monitored channels
    channel_matches_store = False
    
    # Handle stores whether it's a list or a dictionary
    if isinstance(stores, dict):
        # Dictionary format (new)
        for store_id, store in stores.items():
            if store.get('enabled', False) and message.channel.id in store.get('channel_ids', []):
                channel_matches_store = True
                logger.debug(f"Channel {message.channel.name} is in the monitored channels for store {store.get('name', store_id)}")
                break
    elif isinstance(stores, list):
        # List format (legacy)
        for store in stores:
            if isinstance(store, dict) and store.get('enabled', False) and message.channel.id in store.get('channel_ids', []):
                channel_matches_store = True
                logger.debug(f"Channel {message.channel.name} is in the monitored channels for store {store.get('name', 'Unknown')}")
                break
    
    # Also check if the message's category is in our whitelist
    category_match = False
    if hasattr(message.channel, 'category_id') and message.channel.category_id and message.channel.category_id in category_ids:
        category_match = True
        logger.debug(f"Channel {message.channel.name} is in a monitored category")
    
    # If neither the channel matches a store nor the category is monitored, skip
    if not (channel_matches_store or category_match):
        logger.debug(f"Channel {message.channel.name} is not monitored (ID: {message.channel.id})")
        return
        
    # If whitelist is enabled, check if user has a whitelisted role
    # Skip role check for webhooks and app messages
    if whitelist_role_ids and not (message.webhook_id or message.application_id):
        # Convert author's roles to set of IDs for quick lookup
        author_role_ids = {role.id for role in message.author.roles}
        
        # Check if any of the author's roles is in the whitelist
        has_whitelisted_role = any(role_id in author_role_ids for role_id in whitelist_role_ids)
        
        if not has_whitelisted_role:
            logger.debug(f"User {message.author} doesn't have any whitelisted roles")
            return
        
        logger.debug(f"User {message.author} has whitelisted role, processing message")
    
    # Log detailed information about the incoming message
    logger.info(f"Processing message for link reaction from {message.author} in {message.channel.name}")
    
    if message.content:
        content_preview = message.content[:100] + ('...' if len(message.content) > 100 else '')
        logger.info(f"Message content: {content_preview}")
    
    if message.webhook_id:
        logger.info(f"Message is from webhook with ID: {message.webhook_id}")
    elif message.application_id:
        logger.info(f"Message is from application with ID: {message.application_id}")
    
    # Check if message contains embeds from supported stores
    has_supported_store_embed = False
    detected_stores = []
    
    # Get active store configurations
    active_stores = store_manager.get_active_stores()
    
    if message.embeds and active_stores:
        logger.info(f"Message in {message.channel.name} contains {len(message.embeds)} embeds")
        
        for i, embed in enumerate(message.embeds):
            logger.info(f"Embed #{i+1} in message from {message.author}:")
            
            # Check if this embed matches any of our configured stores
            for store_id, store_config in active_stores.items():
                # Match based on detection type
                is_match = False
                detection = store_config.get("detection", {})
                detection_type = detection.get("type", "")
                detection_value = detection.get("value", "")
                
                logger.debug(f"Checking embed against store {store_id} with detection {detection_type}:{detection_value}")
                
                if detection_type == "author_name":
                    if embed.author and embed.author.name and detection_value.lower() in embed.author.name.lower():
                        is_match = True
                        logger.debug(f"Match on author name: {embed.author.name}")
                elif detection_type == "title_contains":
                    if embed.title and detection_value.lower() in embed.title.lower():
                        is_match = True
                        logger.debug(f"Match on title: {embed.title}")
                elif detection_type == "url_contains":
                    if embed.url and detection_value.lower() in embed.url.lower():
                        is_match = True
                        logger.debug(f"Match on URL: {embed.url}")
                # Check fields for matching content
                if not is_match and embed.fields:
                    for field in embed.fields:
                        if (field.name and detection_value.lower() in field.name.lower()) or \
                           (field.value and detection_value.lower() in field.value.lower()):
                            is_match = True
                            logger.debug(f"Match on field content: {field.name} / {field.value}")
                            break
                
                if is_match:
                    logger.info(f"Found supported store embed: {store_config.get('name', store_id)}")
                    has_supported_store_embed = True
                    detected_stores.append(store_id)
                    break  # Found a match for this embed
            
            # Log detailed embed information
            if embed.title:
                logger.info(f"  - Title: {embed.title}")
            if embed.description:
                desc_preview = embed.description[:100] + ('...' if len(embed.description) > 100 else '')
                logger.info(f"  - Description: {desc_preview}")
            if embed.fields:
                logger.info(f"  - Contains {len(embed.fields)} fields")
                for j, field in enumerate(embed.fields):
                    logger.info(f"    - Field #{j+1}: '{field.name}' | Value: '{field.value[:50]}{'...' if len(field.value) > 50 else ''}'")
            if embed.footer:
                logger.info(f"  - Footer: {embed.footer.text if embed.footer.text else 'No text'}")
            if embed.author:
                logger.info(f"  - Author: {embed.author.name if embed.author.name else 'No name'}")
        
        # Log which stores were detected
        if detected_stores:
            logger.info(f"Detected stores: {', '.join(detected_stores)}")
    
    # Also check message content for links from monitored domains
    if message.content:
        for store_id, store_config in active_stores.items():
            detection = store_config.get("detection", {})
            if detection.get("type") == "url_contains":
                domain = detection.get("value", "").lower()
                if domain and domain in message.content.lower():
                    logger.info(f"Found {domain} link in message content")
                    has_supported_store_embed = True
                    if store_id not in detected_stores:
                        detected_stores.append(store_id)
    
    # Only add link reaction if the message contains embeds or links from supported stores
    if not has_supported_store_embed:
        logger.debug(f"Skipping link reaction - no content from supported stores found")
        return
    
    # For webhook/app messages or whitelisted users with supported store embeds:
    logger.info(f"Adding link reaction to message with supported store content")
    
    # Check if this message is also in a category that gets the forward reaction
    # If so, wait 3 seconds to make sure the forward reaction is added first
    # Access CATEGORY_IDS as a property, not a function
    forward_category_ids = forward_config.settings_manager.get("CATEGORY_IDS", [])
    is_forward_category = hasattr(message.channel, 'category_id') and message.channel.category_id in forward_category_ids
    should_delay = False
    
    # Also get ENABLED as a property
    forward_enabled = forward_config.settings_manager.get("ENABLED", False)
    
    if is_forward_category and forward_enabled:
        # This message will also get a forward reaction
        # from the reaction_forward module, so add delay
        logger.debug(f"Message will also get forward reaction, adding delay before link reaction")
        should_delay = True
    
    try:
        # Add the delay if needed
        if should_delay:
            await asyncio.sleep(3)
            
        # Add the link emoji reaction
        link_emoji = config.settings_manager.get("LINK_EMOJI", "🔗")
        await message.add_reaction(link_emoji)
        if message.webhook_id:
            logger.info(f"Added link reaction to webhook message in {message.channel.name}")
        elif message.application_id:
            logger.info(f"Added link reaction to app message in {message.channel.name}")
        else:
            logger.info(f"Added link reaction to message from {message.author} in {message.channel.name}")
    except Exception as e:
        logger.error(f"Failed to add reaction: {str(e)}")

async def handle_reaction_add(reaction, user):
    """
    Handle a reaction being added to a message.
    If the reaction is the link emoji and the user has a whitelisted role,
    check the embed for store-specific information and save PIDs to a file.
    
    Args:
        reaction: The reaction that was added
        user: The user who added the reaction
    """
    # Get configuration directly from settings manager
    enabled = config.settings_manager.get("ENABLED", False)
    link_emoji = config.settings_manager.get("LINK_EMOJI", "🔗")
    whitelist_role_ids = config.settings_manager.get("WHITELIST_ROLE_IDS", [])
    
    # Skip if feature is disabled
    if not enabled:
        return
    
    # Skip if the user is a bot
    if user.bot:
        return
    
    # Get the message that was reacted to
    message = reaction.message
    
    # Skip if not in a guild
    if not message.guild:
        return
    
    # Check if the reaction is the link emoji
    if str(reaction.emoji) != link_emoji:
        return
    
    # Skip if message has no embeds
    if not message.embeds:
        logger.debug(f"Skipping link reaction - message has no embeds")
        return
        
    # Log detailed information about the message that was reacted to
    logger.info(f"User {user} reacted with link emoji to a message with embeds from {message.author} in {message.channel.name}")
    
    # Check if the user has a whitelisted role
    if whitelist_role_ids:
        # Convert user's roles to set of IDs for quick lookup
        user_role_ids = {role.id for role in user.roles}
        
        # Check if any of the user's roles is in the whitelist
        has_whitelisted_role = any(role_id in user_role_ids for role_id in whitelist_role_ids)
        
        if not has_whitelisted_role:
            logger.debug(f"User {user} doesn't have any whitelisted roles to process link reactions")
            return
        
        logger.info(f"User {user} has whitelisted role, processing link reaction")
    
    # Get stores from the config
    stores = config.settings_manager.get("STORES", {})
    
    # Log all embeds in the message
    logger.info(f"Message has {len(message.embeds)} embeds")
    for i, embed in enumerate(message.embeds):
        logger.info(f"--- EMBED #{i+1} BEGIN ---")
        if embed.title:
            logger.info(f"Title: {embed.title}")
        if embed.description:
            logger.info(f"Description: {embed.description}")
        if embed.url:
            logger.info(f"URL: {embed.url}")
        if embed.author:
            logger.info(f"Author: {embed.author.name}")
        if embed.footer:
            logger.info(f"Footer: {embed.footer.text}")
        
        # Log all fields
        if embed.fields:
            logger.info(f"Fields ({len(embed.fields)}):")
            for j, field in enumerate(embed.fields):
                logger.info(f"  Field #{j+1}: {field.name} = {field.value}")
                
        # Log embed as dictionary for complete data
        embed_dict = embed.to_dict()
        logger.info(f"Full embed data: {embed_dict}")
        logger.info(f"--- EMBED #{i+1} END ---")
    
    # Check each store's configuration
    processed = False
    
    # Handle stores whether it's a list or a dictionary
    if isinstance(stores, dict):
        # Dictionary format (new)
        for store_id, store_config in stores.items():
            # Skip if store is disabled
            if not store_config.get('enabled', False):
                continue
            
            store_name = store_config.get('name', store_id)
            
            # Check if channel is in store's specific channels list
            channel_ids = store_config.get('channel_ids', [])
            if channel_ids and message.channel.id in channel_ids:
                logger.info(f"Message channel {message.channel.id} is in {store_name}'s monitored channels")
                processed = True
                
                # Extract PID information from the embed if it's a LuisaViaRoma embed
                if store_name.lower() == "luisaviaroma" and message.embeds:
                    await process_luisaviaroma_embed(message, user, store_config, embed)
    elif isinstance(stores, list):
        # List format (legacy)
        for store_config in stores:
            # Skip if not a dictionary
            if not isinstance(store_config, dict):
                continue
                
            # Skip if store is disabled
            if not store_config.get('enabled', False):
                continue
            
            store_name = store_config.get('name', 'Unknown')
            
            # Check if channel is in store's specific channels list
            channel_ids = store_config.get('channel_ids', [])
            if channel_ids and message.channel.id in channel_ids:
                logger.info(f"Message channel {message.channel.id} is in {store_name}'s monitored channels")
                processed = True
                
                # Extract PID information from the embed if it's a LuisaViaRoma embed
                if store_name.lower() == "luisaviaroma" and message.embeds:
                    for embed in message.embeds:
                        await process_luisaviaroma_embed(message, user, store_config, embed)
    
    if not processed:
        logger.info(f"Message not in any store's monitored channels")

async def process_luisaviaroma_embed(message, user, store_config, embed):
    """
    Process a LuisaViaRoma embed to extract and save the product ID.
    
    Args:
        message: The Discord message containing the embed
        user: The user who reacted to the message
        store_config: The store configuration for LuisaViaRoma
        embed: The Discord embed to process
    """
    # Check for LuisaViaRoma author
    if embed.author and embed.author.name == "LUISAVIAROMA":
        logger.info(f"Found LuisaViaRoma embed")
        
        # Extract PID from URL or PID field
        pid_value = None
        
        # Try URL extraction first
        if embed.url:
            logger.info(f"Trying URL extraction for LuisaViaRoma")
            # Extract from URL pattern
            url_parts = embed.url.split('/')
            if url_parts and len(url_parts) > 1:
                potential_pid = url_parts[-1]
                # Check if it matches LuisaViaRoma PID format (usually has hyphens)
                if '-' in potential_pid:
                    pid_value = potential_pid
                    logger.info(f"Extracted product ID from URL: {pid_value}")
        
        # If URL extraction didn't work, try the PID field
        if not pid_value:
            for field in embed.fields:
                if field.name.upper() == "PID":
                    raw_value = field.value
                    pid_value = raw_value.replace("```", "").strip()
                    logger.info(f"Found PID in field: {pid_value}")
                    break
        
        # If we found a PID, save it to the configured file path
        if pid_value:
            # Get file path from store config - use the user-set path
            store_file_path = store_config.get('file_path')
            
            if store_file_path:
                logger.info(f"Using file path from store configuration: {store_file_path}")
                try:
                    # Check if file exists and if PID is already in the file
                    existing_pids = set()
                    needs_newline = False
                    file_empty = True
                    
                    # Create directory if it doesn't exist
                    os.makedirs(os.path.dirname(os.path.abspath(store_file_path)), exist_ok=True)
                    
                    if os.path.exists(store_file_path) and os.path.getsize(store_file_path) > 0:
                        with open(store_file_path, "r") as f:
                            # Read all existing PIDs
                            existing_content = f.read()
                            existing_pids = {line.strip() for line in existing_content.splitlines() if line.strip()}
                            
                            # Check if file ends with newline
                            needs_newline = not existing_content.endswith('\n')
                            file_empty = not existing_content.strip()
                            
                            logger.debug(f"Found {len(existing_pids)} existing PIDs in file")
                    
                    # Check if PID already exists in the file
                    if pid_value in existing_pids:
                        logger.info(f"PID {pid_value} already exists in file, skipping")
                        await message.channel.send(f"ℹ️ Product ID `{pid_value}` already exists in {store_config.get('name', 'LUISAVIAROMA')} tracking list.")
                        return
                    
                    # Append the PID to the file
                    with open(store_file_path, "a") as f:
                        if needs_newline:
                            f.write(f"\n{pid_value}\n")
                            logger.info(f"Added newline before writing PID")
                        elif file_empty:
                            f.write(f"{pid_value}\n")
                        else:
                            f.write(f"{pid_value}\n")
                    
                    logger.info(f"Successfully added PID {pid_value} to {store_file_path}")
                    
                    # Send confirmation response
                    await message.channel.send(f"✅ Added product ID `{pid_value}` to {store_config.get('name', 'LUISAVIAROMA')} tracking list.")
                except Exception as e:
                    logger.error(f"Failed to write PID to file: {str(e)}")
                    await message.channel.send(f"❌ Error saving product ID: {str(e)}")
            else:
                logger.error(f"No file path configured for {store_config.get('name', 'LUISAVIAROMA')}")
                await message.channel.send(f"❌ Error: {store_config.get('name', 'LUISAVIAROMA')} file path not configured.")
        else:
            logger.warning(f"No product ID found in this {store_config.get('name', 'LUISAVIAROMA')} embed")
            await message.channel.send(f"❌ No product ID found in this {store_config.get('name', 'LUISAVIAROMA')} embed.")

def setup_link_reaction(bot):
    """
    Set up the link reaction feature for a bot.
    
    Args:
        bot: The Discord bot to set up
    """
    logger.info("Setting up link_reaction feature")
    
    # Get configuration directly from settings manager
    enabled = config.settings_manager.get("ENABLED", False)
    category_ids = config.settings_manager.get("CATEGORY_IDS", [])
    blacklist_channel_ids = config.settings_manager.get("BLACKLIST_CHANNEL_IDS", [])
    stores = config.settings_manager.get("STORES", {})
    
    logger.info(f"Link reaction enabled: {enabled}")
    logger.info(f"Whitelisted categories: {category_ids}")
    logger.info(f"Blacklisted channels: {blacklist_channel_ids}")
    
    # Log the stores configuration
    all_monitored_channels = set()
    
    # Handle stores whether it's a list or a dictionary
    logger.info(f"Stores data type: {type(stores).__name__}")
    
    if isinstance(stores, dict):
        # Dictionary format (new)
        for store_id, store in stores.items():
            if store.get('enabled', False):
                store_name = store.get('name', store_id)
                file_path = store.get('file_path', 'Not configured')
                channel_ids = store.get('channel_ids', [])
                all_monitored_channels.update(channel_ids)
                
                # Log the detection method
                detection = store.get('detection', {})
                detection_type = detection.get('type', 'None')
                detection_value = detection.get('value', 'None')
                
                logger.info(f"Store configured: {store_name}")
                logger.info(f"  - File path: {file_path}")
                logger.info(f"  - Channel IDs: {channel_ids}")
                logger.info(f"  - Detection: {detection_type}:{detection_value}")
    elif isinstance(stores, list):
        # List format (legacy)
        for store in stores:
            if isinstance(store, dict) and store.get('enabled', False):
                store_name = store.get('name', 'Unknown')
                file_path = store.get('file_path', 'Not configured')
                channel_ids = store.get('channel_ids', [])
                all_monitored_channels.update(channel_ids)
                
                logger.info(f"Store configured (legacy format): {store_name}")
                logger.info(f"  - File path: {file_path}")
                logger.info(f"  - Channel IDs: {channel_ids}")
    else:
        logger.warning(f"Unknown stores data type: {type(stores).__name__}")
    
    logger.info(f"Total unique monitored channels: {len(all_monitored_channels)}")
    
    # Check if we have monitored channels or categories
    if not (all_monitored_channels or category_ids):
        logger.warning("No monitored channels or categories configured! Link reactions will not be added.")
    
    # Store the original message handler to call later
    original_message_handler = bot.event_handlers.get('on_message', None) if hasattr(bot, 'event_handlers') else None
    
    # Create our message handler to process both link reactions and call the original handler
    @bot.listen('on_message')
    async def on_message_link_reaction(message):
        # Process the message for link reactions
        await process_message(message)
        
        # No need to call process_commands as the original handler will do that
    
    # Listen for reaction add events (using listen() instead of overriding the original handler)
    @bot.listen('on_reaction_add')
    async def on_reaction_add_link_reaction(reaction, user):
        # Process the reaction for link reaction feature
        await handle_reaction_add(reaction, user) 