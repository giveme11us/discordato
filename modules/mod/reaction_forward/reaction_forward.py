"""
Reaction Forward Feature

This module monitors messages in specified categories
and adds a forward arrow reaction to them.
It also allows users with whitelisted roles to forward messages
to the notification channel by reacting with the forward arrow.
"""

import logging
import discord
import os
import asyncio
from config import reaction_forward_config as config
from config import pinger_config
from config import embed_config

logger = logging.getLogger('discord_bot.modules.mod.reaction_forward')

# Define emoji for forwarding
forward_emoji = "➡️"

async def process_message(message):
    """
    Process a message to check if it's in a whitelisted category.
    If it is, add a forward arrow reaction.
    
    Args:
        message: The Discord message to process
    """
    # Get settings directly from settings manager
    enabled = config.settings_manager.get("ENABLED", False)
    category_ids_raw = config.settings_manager.get("CATEGORY_IDS", [])
    
    # Make sure category_ids is a list of integers
    category_ids = []
    for cat_id in category_ids_raw:
        try:
            if isinstance(cat_id, str) and cat_id.isdigit():
                category_ids.append(int(cat_id))
            elif isinstance(cat_id, int):
                category_ids.append(cat_id)
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid category ID in settings: {cat_id} - {e}")
    
    blacklist_channel_ids = config.settings_manager.get("BLACKLIST_CHANNEL_IDS", [])
    forward_emoji = config.settings_manager.get("FORWARD_EMOJI", "➡️")
    
    # Log detailed debug information on every message
    if hasattr(message.channel, 'name') and hasattr(message.channel, 'category_id'):
        logger.debug(f"Processing message in channel: {message.channel.name}, category_id: {message.channel.category_id}")
        logger.debug(f"Enabled: {enabled}, Category IDs: {category_ids}")
    
    # Skip if feature is disabled
    if not enabled:
        logger.debug("Feature is disabled, skipping")
        return
    
    # Skip if no categories are configured
    if not category_ids:
        logger.debug("No category IDs configured for reaction_forward feature")
        return
    
    # Skip messages from bots, but allow webhook/integration messages
    if message.author.bot and not (message.webhook_id or message.application_id):
        logger.debug(f"Skipping message from bot (non-webhook): {message.author}")
        return
    
    # Skip messages that are likely forwarded messages from our own webhook
    if message.webhook_id and message.author.name and ("Forwarded" in message.author.name or "forwarded" in message.author.name):
        logger.debug(f"Skipping likely forwarded message from webhook: {message.author.name}")
        return
    
    # Skip if not in a guild or not in a channel with a category
    if not message.guild or not hasattr(message.channel, 'category_id') or not message.channel.category_id:
        logger.debug("Message not in guild or channel has no category")
        return
    
    # Skip if the channel is in the blacklist
    if message.channel.id in blacklist_channel_ids:
        logger.debug(f"Skipping message in blacklisted channel: {message.channel.name}")
        return
    
    # Skip if the channel is the pinger notification channel to avoid loops
    notification_channel_id = pinger_config.settings_manager.get("NOTIFICATION_CHANNEL_ID")
    if message.channel.id == notification_channel_id:
        logger.debug(f"Skipping message in notification channel (ID: {notification_channel_id})")
        return
    
    # Debug the category check
    logger.debug(f"Message category ID: {message.channel.category_id}, Whitelist: {category_ids}")
    category_match = message.channel.category_id in category_ids
    logger.debug(f"Category match result: {category_match}")
    
    # Check if the message's category is in our whitelist
    if category_match:
        logger.debug(f"Message in category {message.channel.category_id} matches whitelisted categories: {category_ids}")
        
        try:
            # Log the incoming message information for tracking
            logger.debug(f"Processing message: {message.id} from {message.author} in {message.channel.name}")
            logger.debug(f"Message content: {message.content[:50]}{'...' if len(message.content) > 50 else ''}")
            
            # Log additional details for webhooks and apps
            if message.webhook_id:
                logger.debug(f"Message is from webhook with ID: {message.webhook_id}")
            elif message.application_id:
                logger.debug(f"Message is from application with ID: {message.application_id}")
            
            # Log content summary for debugging
            if message.embeds:
                logger.debug(f"Message has {len(message.embeds)} embeds")
            if message.attachments:
                logger.debug(f"Message has {len(message.attachments)} attachments")
            if message.reference:
                logger.debug(f"Message is a reply to message ID: {message.reference.message_id}")
        except Exception as e:
            logger.error(f"Error logging incoming message data: {str(e)}")
        
        # Check if the message has embeds - only react if it does
        if not message.embeds:
            logger.debug(f"Skipping reaction - message has no embeds")
            return
            
        # For webhook/app messages or whitelisted users:
        logger.debug(f"Adding forward reaction to message with embeds in category {message.channel.category}")
        try:
            # Add the forward arrow reaction
            await message.add_reaction(forward_emoji)
            if message.webhook_id:
                logger.info(f"Added forward reaction to webhook message with embeds in {message.channel.name}")
            elif message.application_id:
                logger.info(f"Added forward reaction to app message with embeds in {message.channel.name}")
            else:
                logger.info(f"Added forward reaction to message with embeds from {message.author} in {message.channel.name}")
        except Exception as e:
            logger.error(f"Failed to add reaction: {str(e)}")
    else:
        logger.debug(f"Message in category {message.channel.category_id} does not match any whitelisted categories: {category_ids}")

async def handle_reaction_add(reaction, user):
    """
    Handle a reaction being added to a message.
    If the reaction is the forward emoji and the user has a whitelisted role,
    forward the message to the notification channel using Discord's native message forwarding feature.
    
    Args:
        reaction: The reaction that was added
        user: The user who added the reaction
    """
    # Get settings directly from settings manager
    enabled = config.settings_manager.get("ENABLED", False)
    enable_forwarding = config.settings_manager.get("ENABLE_FORWARDING", False)
    forward_emoji = config.settings_manager.get("FORWARD_EMOJI", "➡️")
    whitelist_role_ids = config.settings_manager.get("WHITELIST_ROLE_IDS", [])
    forward_title = config.settings_manager.get("FORWARD_TITLE", "Forwarded Message")
    destination_channel_id = config.settings_manager.get("DESTINATION_CHANNEL_ID")
    forward_attachments = config.settings_manager.get("FORWARD_ATTACHMENTS", True)
    forward_embeds = config.settings_manager.get("FORWARD_EMBEDS", True)
    
    # Fall back to pinger notification channel if destination channel not set
    if not destination_channel_id:
        destination_channel_id = pinger_config.settings_manager.get("NOTIFICATION_CHANNEL_ID")
    
    # Skip if feature is disabled
    if not enabled:
        return
    
    # Skip if forwarding is disabled
    if not enable_forwarding:
        return
    
    # Skip if the user is a bot
    if user.bot:
        return
    
    # Get the message that was reacted to
    message = reaction.message
    
    # Skip if not in a guild
    if not message.guild:
        return
    
    # Check if the reaction is the forward emoji
    if str(reaction.emoji) != forward_emoji:
        return
    
    # Log detailed information about the message being forwarded
    logger.info(f"Forward reaction added by {user} to message from {message.author} in {message.channel.name}")
    logger.info(f"Message content: {message.content[:100]}{'...' if len(message.content) > 100 else ''}")
    
    # Check if the user has a whitelisted role
    if whitelist_role_ids:
        # Convert user's roles to set of IDs for quick lookup
        user_role_ids = {role.id for role in user.roles}
        
        # Check if any of the user's roles is in the whitelist
        has_whitelisted_role = any(role_id in user_role_ids for role_id in whitelist_role_ids)
        
        if not has_whitelisted_role:
            logger.debug(f"User {user} doesn't have any whitelisted roles to forward messages")
            return
        
        logger.info(f"User {user} has whitelisted role, forwarding message")
    
    # Get the notification channel from destination channel ID
    if not destination_channel_id:
        logger.warning("No destination channel configured - cannot forward message")
        return
    
    # Get the destination channel
    destination_channel = message.guild.get_channel(destination_channel_id)
    if not destination_channel:
        logger.warning(f"Destination channel with ID {destination_channel_id} not found")
        return
    
    try:
        # Use Discord's official message forwarding feature
        # Create the webhook to send the message
        webhooks = await destination_channel.webhooks()
        webhook = None
        
        # Look for an existing webhook we can use
        for existing_webhook in webhooks:
            if existing_webhook.user.id == message.guild.me.id and existing_webhook.name == "MessageForwarder":
                webhook = existing_webhook
                break
        
        # Create a new webhook if needed
        if webhook is None:
            webhook = await destination_channel.create_webhook(name="MessageForwarder", reason="For message forwarding feature")
        
        # Forward the message using the webhook
        # This preserves the original author's name and avatar
        # Determine appropriate username and avatar based on message source
        if message.webhook_id:
            forward_username = f"{message.author.display_name} (Forwarded webhook message)"
        elif message.application_id:
            forward_username = f"{message.author.display_name} (Forwarded app message)"
        else:
            forward_username = f"{message.author.display_name} (Forwarded message)"
        
        # Log detailed information about embeds if present
        if message.embeds:
            logger.info(f"Message contains {len(message.embeds)} embeds to forward")
            for i, embed in enumerate(message.embeds):
                logger.info(f"Embed #{i+1} details:")
                if embed.title:
                    logger.info(f"  - Title: {embed.title}")
                if embed.description:
                    logger.info(f"  - Description: {embed.description[:100]}{'...' if len(embed.description) > 100 else ''}")
                if embed.fields:
                    logger.info(f"  - Fields: {len(embed.fields)}")
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
                logger.info(f"  - Color: {embed.color}")
                logger.info(f"  - Timestamp: {embed.timestamp}")
                logger.info(f"  - URL: {embed.url}")
        
        # Log attachments information
        if message.attachments:
            logger.info(f"Message contains {len(message.attachments)} attachments to forward")
            for i, attachment in enumerate(message.attachments):
                logger.info(f"Attachment #{i+1}: {attachment.filename} ({attachment.size} bytes, {attachment.content_type})")
        
        # Send the message
        await webhook.send(
            content=message.content,
            username=forward_username,
            avatar_url=message.author.display_avatar.url,
            wait=True,
            allowed_mentions=discord.AllowedMentions.none(),
            files=[await a.to_file() for a in message.attachments] if message.attachments else [],
            embeds=message.embeds if message.embeds else []
        )
        
        # Add a Jump to Original button in the channel
        view = discord.ui.View()
        button = discord.ui.Button(
            style=discord.ButtonStyle.link,
            label="Jump to Original Message",
            url=message.jump_url
        )
        view.add_item(button)
        
        # Send only the Jump to Original button without the attribution embed
        await destination_channel.send(
            view=view
        )
        
        logger.info(f"Message from {message.author} forwarded to {destination_channel.name} by {user}")
    except discord.errors.HTTPException as e:
        logger.error(f"Failed to forward message: {str(e)}")
        
        # Fallback mechanism if webhooks don't work
        try:
            # Use message.jump_url as a direct link to the original
            embed = discord.Embed(
                title="Forwarded Message",
                description=message.content
            )
            
            # Apply styling from embed_config
            embed = embed_config.apply_default_styling(embed)
            
            # Add author info with source indication
            if message.webhook_id:
                author_name = f"{message.author.display_name} (webhook)"
            elif message.application_id:
                author_name = f"{message.author.display_name} (app)"
            else:
                author_name = message.author.display_name
                
            embed.set_author(
                name=author_name,
                icon_url=message.author.display_avatar.url
            )
            
            # Add footer with forwarding info
            embed.set_footer(text=f"Forwarded from #{message.channel.name}")
            
            # Add timestamp
            embed.timestamp = message.created_at
            
            # Create a Jump to Original button for fallback
            fallback_view = discord.ui.View()
            button = discord.ui.Button(
                style=discord.ButtonStyle.link,
                label="Jump to Original Message",
                url=message.jump_url
            )
            fallback_view.add_item(button)
            
            # Send the original message content in an embed
            await destination_channel.send(
                embed=embed,
                view=fallback_view,
                allowed_mentions=discord.AllowedMentions.none()
            )
            
            # Handle attachments in fallback mode
            if message.attachments:
                for attachment in message.attachments:
                    try:
                        file = await attachment.to_file()
                        await destination_channel.send(file=file)
                    except:
                        await destination_channel.send(f"[Attachment: {attachment.filename}]({attachment.url})")
            
            # Forward embeds if any
            if message.embeds:
                logger.info(f"Attempting to forward {len(message.embeds)} embeds using fallback method")
                for i, embed in enumerate(message.embeds):
                    # Log detailed embed structure for debugging
                    logger.info(f"Fallback embed #{i+1} structure:")
                    embed_dict = embed.to_dict()
                    logger.info(f"Embed as dict: {embed_dict}")
                    
                    # Log each component of the embed
                    if embed.title:
                        logger.info(f"  - Title: {embed.title}")
                    if embed.description:
                        logger.info(f"  - Description: {embed.description[:100]}{'...' if len(embed.description) > 100 else ''}")
                    if embed.fields:
                        logger.info(f"  - Fields: {len(embed.fields)}")
                        for j, field in enumerate(embed.fields):
                            logger.info(f"    - Field #{j+1}: '{field.name}' | Value: '{field.value[:50]}{'...' if len(field.value) > 50 else ''}'")
                    
                    await destination_channel.send(embed=embed)
                    logger.info(f"Successfully forwarded embed #{i+1}")
            
            logger.info(f"Used fallback method to forward message from {message.author}")
        except Exception as fallback_error:
            logger.error(f"Failed to use fallback forwarding method: {str(fallback_error)}")

def setup_reaction_forward(bot):
    """
    Set up the reaction forward feature.
    
    Args:
        bot: The Discord bot instance
    """
    logger.info("Setting up reaction_forward feature")
    
    # Get settings directly from settings manager
    enabled = config.settings_manager.get("ENABLED", False)
    enable_forwarding = config.settings_manager.get("ENABLE_FORWARDING", False)
    
    # Make sure category_ids is a list of integers
    category_ids_raw = config.settings_manager.get("CATEGORY_IDS", [])
    category_ids = []
    for cat_id in category_ids_raw:
        try:
            if isinstance(cat_id, str) and cat_id.isdigit():
                category_ids.append(int(cat_id))
            elif isinstance(cat_id, int):
                category_ids.append(cat_id)
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid category ID in settings: {cat_id} - {e}")
    
    # Store the processed category_ids back to settings
    config.settings_manager.set("CATEGORY_IDS", category_ids)
            
    blacklist_channel_ids = config.settings_manager.get("BLACKLIST_CHANNEL_IDS", [])
    destination_channel_id = config.settings_manager.get("DESTINATION_CHANNEL_ID")
    
    # Fall back to pinger notification channel if destination channel not set
    if not destination_channel_id:
        destination_channel_id = pinger_config.settings_manager.get("NOTIFICATION_CHANNEL_ID")
    
    # Log the configuration with detailed type information
    logger.info(f"Reaction forward enabled: {enabled}")
    logger.info(f"Message forwarding enabled: {enable_forwarding}")
    logger.info(f"Raw category IDs from settings: {category_ids_raw} (type: {type(category_ids_raw).__name__})")
    logger.info(f"Processed category IDs: {category_ids} (type: {type(category_ids).__name__})")
    logger.info(f"Blacklisted channels: {blacklist_channel_ids}")
    logger.info(f"Using destination channel ID: {destination_channel_id}")
    
    # Use listen instead of event to avoid overriding other handlers
    @bot.listen('on_message')
    async def on_message_reaction_forward(message):
        # Process the message for the reaction_forward feature
        await process_message(message)
        
        # No need to call bot.process_commands() here - the main handler will do that
    
    # Use listen instead of event to avoid overriding other handlers
    @bot.listen('on_reaction_add')
    async def on_reaction_add_reaction_forward(reaction, user):
        # Process the reaction for forwarding messages
        await handle_reaction_add(reaction, user) 