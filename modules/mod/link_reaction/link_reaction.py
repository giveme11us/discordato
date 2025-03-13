"""
Link Reaction Feature

This module monitors messages in specified categories
and adds a link emoji reaction to them.
"""

import logging
import discord
import asyncio
from config import link_reaction_config as config
from config import pinger_config
from config import reaction_forward_config as forward_config
import os
import re

logger = logging.getLogger('discord_bot.modules.mod.link_reaction')

async def process_message(message):
    """
    Process a message to check if it's in a whitelisted category.
    If it is, add a link emoji reaction.
    
    Args:
        message: The Discord message to process
    """
    # Skip if feature is disabled
    if not config.ENABLED:
        return
    
    # Skip if no categories are configured
    if not config.CATEGORY_IDS:
        logger.debug("No category IDs configured for link_reaction feature")
        return
    
    # Skip messages from bots, but allow webhook/integration messages
    if message.author.bot and not (message.webhook_id or message.application_id):
        logger.debug(f"Skipping message from bot (non-webhook): {message.author}")
        return
    
    # Skip if not in a guild or not in a channel with a category
    if not message.guild or not message.channel.category_id:
        return
    
    # Skip if the channel is in the blacklist
    if message.channel.id in config.BLACKLIST_CHANNEL_IDS:
        logger.debug(f"Skipping message in blacklisted channel: {message.channel.name}")
        return
    
    # Skip if the channel is the notification channel
    notification_channel_id = pinger_config.NOTIFICATION_CHANNEL_ID
    if message.channel.id == notification_channel_id:
        logger.debug(f"Skipping message in notification channel")
        return
    
    # Check if the message's category is in our whitelist
    if message.channel.category_id in config.CATEGORY_IDS:
        # If whitelist is enabled, check if user has a whitelisted role
        # Skip role check for webhooks and app messages
        if config.WHITELIST_ROLE_IDS and not (message.webhook_id or message.application_id):
            # Convert author's roles to set of IDs for quick lookup
            author_role_ids = {role.id for role in message.author.roles}
            
            # Check if any of the author's roles is in the whitelist
            has_whitelisted_role = any(role_id in author_role_ids for role_id in config.WHITELIST_ROLE_IDS)
            
            if not has_whitelisted_role:
                logger.debug(f"User {message.author} doesn't have any whitelisted roles")
                return
            
            logger.debug(f"User {message.author} has whitelisted role, processing message")
        
        # Log detailed information about the incoming message
        logger.info(f"Processing message for link reaction from {message.author} in {message.channel.name}")
        logger.info(f"Message full content: {message.content}")
        logger.info(f"Message ID: {message.id} | Channel: {message.channel.name} | Category: {message.channel.category.name}")
        
        if message.webhook_id:
            logger.info(f"Message is from webhook with ID: {message.webhook_id}")
        elif message.application_id:
            logger.info(f"Message is from application with ID: {message.application_id}")
        
        # Log message reference if it exists (for replies)
        if message.reference:
            logger.info(f"Message is a reply to message ID: {message.reference.message_id}")
        
        # Log more details about the message content
        if message.embeds:
            logger.info(f"Message in {message.channel.name} contains {len(message.embeds)} embeds")
            for i, embed in enumerate(message.embeds):
                logger.info(f"Embed #{i+1} in message from {message.author}:")
                # Log the raw embed data as dictionary
                logger.info(f"Raw embed data: {embed.to_dict()}")
                
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
                if embed.image:
                    logger.info(f"  - Has image: {embed.image.url if embed.image.url else 'No URL'}")
                if embed.thumbnail:
                    logger.info(f"  - Has thumbnail: {embed.thumbnail.url if embed.thumbnail.url else 'No URL'}")
                
        if message.attachments:
            logger.info(f"Message in {message.channel.name} contains {len(message.attachments)} attachments")
            for i, attachment in enumerate(message.attachments):
                logger.info(f"Attachment #{i+1}: {attachment.filename} ({attachment.content_type})")
                logger.info(f"  - Size: {attachment.size} bytes | URL: {attachment.url}")
                logger.info(f"  - Dimensions: {attachment.width}x{attachment.height}" if hasattr(attachment, 'width') and attachment.width else "  - No dimensions available")
        
        # For webhook/app messages or whitelisted users:
        logger.debug(f"Adding link reaction to message in category {message.channel.category}")
        
        # Check if this message is also in a category that gets the forward reaction
        # If so, wait 3 seconds to make sure the forward reaction is added first
        is_forward_category = message.channel.category_id in forward_config.CATEGORY_IDS
        should_delay = False
        
        if is_forward_category and forward_config.ENABLED:
            # This message will also get a forward reaction
            # from the reaction_forward module, so add delay
            logger.debug(f"Message will also get forward reaction, adding delay before link reaction")
            should_delay = True
        
        try:
            # Add the delay if needed
            if should_delay:
                await asyncio.sleep(3)
                
            # Add the link emoji reaction
            await message.add_reaction(config.LINK_EMOJI)
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
    # Skip if feature is disabled
    if not config.ENABLED:
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
    if str(reaction.emoji) != config.LINK_EMOJI:
        return
    
    # Log detailed information about the message that was reacted to
    logger.info(f"User {user} reacted with link emoji to a message from {message.author} in {message.channel.name}")
    logger.info(f"Message content: {message.content[:100]}{'...' if len(message.content) > 100 else ''}")
    
    # Check if the user has a whitelisted role
    if config.WHITELIST_ROLE_IDS:
        # Convert user's roles to set of IDs for quick lookup
        user_role_ids = {role.id for role in user.roles}
        
        # Check if any of the user's roles is in the whitelist
        has_whitelisted_role = any(role_id in user_role_ids for role_id in config.WHITELIST_ROLE_IDS)
        
        if not has_whitelisted_role:
            logger.debug(f"User {user} doesn't have any whitelisted roles to process link reactions")
            return
        
        logger.info(f"User {user} has whitelisted role, processing link reaction")
    
    # Log information about embeds if present
    if message.embeds:
        logger.info(f"Reacted message contains {len(message.embeds)} embeds")
        
        # Check for store-specific embeds and process them
        for i, embed in enumerate(message.embeds):
            logger.info(f"Embed #{i+1} details:")
            logger.info(f"  - To dict representation: {embed.to_dict()}")
            
            # Log all embed components for debugging
            if embed.title:
                logger.info(f"  - Title: {embed.title}")
            if embed.description:
                logger.info(f"  - Description: {embed.description[:100]}{'...' if len(embed.description) > 100 else ''}")
            if embed.author:
                logger.info(f"  - Author: {embed.author.name if embed.author.name else 'No name'}")
            if embed.fields:
                logger.info(f"  - Fields: {len(embed.fields)}")
                for j, field in enumerate(embed.fields):
                    logger.info(f"    - Field #{j+1}: '{field.name}' | Value: '{field.value[:50]}{'...' if len(field.value) > 50 else ''}'")
            
            # Check if this is a LUISAVIAROMA embed
            if embed.author and embed.author.name == "LUISAVIAROMA":
                logger.info(f"Found LUISAVIAROMA embed in message")
                
                # Look for URL first
                pid_value = None
                embed_url = embed.url
                
                if embed_url and 'luisaviaroma.com' in embed_url:
                    logger.info(f"Found LUISAVIAROMA URL: {embed_url}")
                    
                    # Parse the URL to extract the product ID
                    # Example URL format: https://www.luisaviaroma.com/en-it/p/sneakers/81I-ZM5016
                    pattern = r'\/[^\/]+\/([^\/]+)$'  # Match the last segment after the last slash, preceded by another segment
                    match = re.search(pattern, embed_url)
                    
                    if match:
                        pid_value = match.group(1)
                        logger.info(f"Extracted product ID from URL: {pid_value}")
                    else:
                        # If URL pattern doesn't match, try a simpler approach
                        url_parts = embed_url.split('/')
                        if url_parts and len(url_parts) > 1:
                            potential_pid = url_parts[-1]
                            # Validate that it looks like a PID (typically has format like 81I-ZM5016)
                            if '-' in potential_pid and len(potential_pid) > 4:
                                pid_value = potential_pid
                                logger.info(f"Extracted product ID using fallback method: {pid_value}")
                
                # If URL parsing failed, check for PID field as fallback
                if not pid_value:
                    logger.info("URL parsing failed, trying to extract from PID field")
                    for field in embed.fields:
                        if field.name.upper() == "PID":
                            # Extract the PID value and clean it
                            raw_value = field.value
                            # Remove markdown formatting (```\n...\n```)
                            pid_value = raw_value.replace("```", "").strip()
                            logger.info(f"Found PID in LUISAVIAROMA embed field: {pid_value}")
                            break
                
                if pid_value:
                    # Get the path from environment variable
                    lv_file_path = os.getenv("luisaviaroma_drops_urls_path")
                    
                    if lv_file_path:
                        try:
                            # Append the PID to the file
                            with open(lv_file_path, "a") as f:
                                f.write(f"{pid_value}\n")
                            logger.info(f"Successfully added PID {pid_value} to {lv_file_path}")
                            
                            # Send confirmation response
                            await message.channel.send(f"✅ Added product ID `{pid_value}` to LUISAVIAROMA tracking list.")
                        except Exception as e:
                            logger.error(f"Failed to write PID to file: {str(e)}")
                            await message.channel.send(f"❌ Error saving product ID: {str(e)}")
                    else:
                        logger.error("LUISAVIAROMA file path not configured in environment variables")
                        await message.channel.send("❌ Error: LUISAVIAROMA file path not configured.")
                else:
                    logger.warning("No PID field found in LUISAVIAROMA embed")
                    await message.channel.send("❌ No product ID found in this embed.")
    
    # Log information about attachments if present
    if message.attachments:
        logger.info(f"Reacted message contains {len(message.attachments)} attachments")
        for i, attachment in enumerate(message.attachments):
            logger.info(f"Attachment #{i+1}: {attachment.filename} ({attachment.size} bytes, {attachment.content_type})")
    
    logger.debug(f"Link reaction processing completed")

def setup_link_reaction(bot):
    """
    Set up the link reaction feature.
    
    Args:
        bot: The Discord bot instance
    """
    logger.info("Setting up link_reaction feature")
    
    # Log the configuration
    logger.info(f"Link reaction enabled: {config.ENABLED}")
    logger.info(f"Whitelisted categories: {config.CATEGORY_IDS}")
    logger.info(f"Blacklisted channels: {config.BLACKLIST_CHANNEL_IDS}")
    
    # Log store-specific drop file paths
    lv_file_path = os.getenv("luisaviaroma_drops_urls_path")
    if lv_file_path:
        logger.info(f"LUISAVIAROMA drops will be saved to: {lv_file_path}")
    else:
        logger.warning("LUISAVIAROMA drops file path not configured in environment variables")
    
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