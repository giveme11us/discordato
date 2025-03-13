"""
Reaction Forward Feature

This module monitors messages in specified categories
and adds a forward arrow reaction to them.
It also allows users with whitelisted roles to forward messages
to the notification channel by reacting with the forward arrow.
"""

import logging
import discord
from config import reaction_forward_config as config
from config import pinger_config

logger = logging.getLogger('discord_bot.modules.mod.reaction_forward')

async def process_message(message):
    """
    Process a message to check if it's in a whitelisted category.
    If it is, add a forward arrow reaction.
    
    Args:
        message: The Discord message to process
    """
    # Skip if feature is disabled
    if not config.ENABLED:
        return
    
    # Skip if no categories are configured
    if not config.CATEGORY_IDS:
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
    if not message.guild or not message.channel.category_id:
        return
    
    # Skip if the channel is in the blacklist
    if message.channel.id in config.BLACKLIST_CHANNEL_IDS:
        logger.debug(f"Skipping message in blacklisted channel: {message.channel.name}")
        return
    
    # Skip if the channel is the notification channel (to avoid adding reactions to forwarded messages)
    notification_channel_id = pinger_config.NOTIFICATION_CHANNEL_ID
    if message.channel.id == notification_channel_id:
        logger.debug(f"Skipping message in notification channel to avoid reaction loops")
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
        logger.info(f"Processing new message in whitelisted category from {message.author} in {message.channel.name}")
        logger.info(f"Full message content: {message.content}")
        logger.info(f"Message ID: {message.id} | Channel: {message.channel.name} | Category: {message.channel.category.name}")
        
        # Log additional message metadata
        if message.webhook_id:
            logger.info(f"Message is from webhook with ID: {message.webhook_id}")
        elif message.application_id:
            logger.info(f"Message is from application with ID: {message.application_id}")
        
        # Log message reference if it exists (for replies)
        if message.reference:
            logger.info(f"Message is a reply to message ID: {message.reference.message_id}")
        
        # Get message data as dict for debugging
        message_data = {
            'id': message.id,
            'content_length': len(message.content),
            'author': str(message.author),
            'channel': str(message.channel),
            'created_at': str(message.created_at),
            'embeds_count': len(message.embeds),
            'attachments_count': len(message.attachments),
            'reference': str(message.reference) if message.reference else None,
        }
        logger.info(f"Message metadata: {message_data}")
        
        # Log raw message data for debugging
        try:
            # Log embed information if present
            if message.embeds:
                logger.info(f"Incoming message contains {len(message.embeds)} embeds")
                for i, embed in enumerate(message.embeds):
                    logger.info(f"Incoming embed #{i+1} details:")
                    embed_dict = embed.to_dict()
                    logger.info(f"Embed raw data: {embed_dict}")
                    
                    if embed.title:
                        logger.info(f"  - Title: {embed.title}")
                    if embed.description:
                        logger.info(f"  - Description: {embed.description[:100]}{'...' if len(embed.description) > 100 else ''}")
                    if embed.fields:
                        logger.info(f"  - Fields: {len(embed.fields)}")
                        for j, field in enumerate(embed.fields):
                            logger.info(f"    - Field #{j+1}: '{field.name}' | Value: '{field.value[:50]}{'...' if len(field.value) > 50 else ''}'")
            
            # Log attachment information if present
            if message.attachments:
                logger.info(f"Incoming message contains {len(message.attachments)} attachments")
                for i, attachment in enumerate(message.attachments):
                    logger.info(f"Attachment #{i+1}: {attachment.filename} ({attachment.size} bytes, {attachment.content_type})")
        except Exception as e:
            logger.error(f"Error logging incoming message data: {str(e)}")
        
        # For webhook/app messages or whitelisted users:
        logger.debug(f"Adding forward reaction to message in category {message.channel.category}")
        try:
            # Add the forward arrow reaction
            await message.add_reaction(config.FORWARD_EMOJI)
            if message.webhook_id:
                logger.info(f"Added forward reaction to webhook message in {message.channel.name}")
            elif message.application_id:
                logger.info(f"Added forward reaction to app message in {message.channel.name}")
            else:
                logger.info(f"Added forward reaction to message from {message.author} in {message.channel.name}")
        except Exception as e:
            logger.error(f"Failed to add reaction: {str(e)}")

async def handle_reaction_add(reaction, user):
    """
    Handle a reaction being added to a message.
    If the reaction is the forward emoji and the user has a whitelisted role,
    forward the message to the notification channel using Discord's native message forwarding feature.
    
    Args:
        reaction: The reaction that was added
        user: The user who added the reaction
    """
    # Skip if feature is disabled
    if not config.ENABLED:
        return
    
    # Skip if forwarding is disabled
    if not config.ENABLE_FORWARDING:
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
    if str(reaction.emoji) != config.FORWARD_EMOJI:
        return
    
    # Log detailed information about the message being forwarded
    logger.info(f"Forward reaction added by {user} to message from {message.author} in {message.channel.name}")
    logger.info(f"Message content: {message.content[:100]}{'...' if len(message.content) > 100 else ''}")
    
    # Log raw message data for debugging
    try:
        # Get message data as dict for debugging
        message_data = {
            'id': message.id,
            'content': message.content[:200] + ('...' if len(message.content) > 200 else ''),
            'author': str(message.author),
            'channel': str(message.channel),
            'created_at': str(message.created_at),
            'embeds_count': len(message.embeds),
            'attachments_count': len(message.attachments),
            'reference': str(message.reference) if message.reference else None,
        }
        logger.info(f"Message data: {message_data}")
        
        # Log embed raw data
        if message.embeds:
            logger.info(f"Message contains {len(message.embeds)} embeds to be forwarded")
            for i, embed in enumerate(message.embeds):
                embed_dict = embed.to_dict()
                logger.info(f"Raw embed #{i+1} data: {embed_dict}")
                
                # Log specific embed components in a more readable format
                logger.info(f"Embed #{i+1} components:")
                if embed.title:
                    logger.info(f"  - Title: {embed.title}")
                if embed.description:
                    logger.info(f"  - Description: {embed.description[:100]}{'...' if len(embed.description) > 100 else ''}")
                if embed.fields:
                    for j, field in enumerate(embed.fields):
                        logger.info(f"  - Field #{j+1}: '{field.name}' = '{field.value[:50]}{'...' if len(field.value) > 50 else ''}'")
                if embed.footer:
                    logger.info(f"  - Footer: {embed.footer.text}")
                if embed.author:
                    logger.info(f"  - Author: {embed.author.name}")
                    logger.info(f"    - Author icon: {embed.author.icon_url}")
                if embed.image:
                    logger.info(f"  - Image URL: {embed.image.url}")
                if embed.thumbnail:
                    logger.info(f"  - Thumbnail URL: {embed.thumbnail.url}")
    except Exception as e:
        logger.error(f"Error logging message data: {str(e)}")
    
    # Check if the user has a whitelisted role
    if config.WHITELIST_ROLE_IDS:
        # Convert user's roles to set of IDs for quick lookup
        user_role_ids = {role.id for role in user.roles}
        
        # Check if any of the user's roles is in the whitelist
        has_whitelisted_role = any(role_id in user_role_ids for role_id in config.WHITELIST_ROLE_IDS)
        
        if not has_whitelisted_role:
            logger.debug(f"User {user} doesn't have any whitelisted roles to forward messages")
            return
        
        logger.debug(f"User {user} has whitelisted role, processing forward request")
    
    # Get the notification channel ID from pinger config
    notification_channel_id = pinger_config.NOTIFICATION_CHANNEL_ID
    if not notification_channel_id:
        logger.warning("No notification channel configured - cannot forward message")
        return
    
    # Get the notification channel
    notification_channel = message.guild.get_channel(notification_channel_id)
    if not notification_channel:
        logger.warning(f"Notification channel with ID {notification_channel_id} not found")
        return
    
    try:
        # Use Discord's official message forwarding feature
        # Create the webhook to send the message
        webhooks = await notification_channel.webhooks()
        webhook = None
        
        # Look for an existing webhook we can use
        for existing_webhook in webhooks:
            if existing_webhook.user.id == message.guild.me.id and existing_webhook.name == "MessageForwarder":
                webhook = existing_webhook
                break
        
        # Create a new webhook if needed
        if webhook is None:
            webhook = await notification_channel.create_webhook(name="MessageForwarder", reason="For message forwarding feature")
        
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
        
        # First option (preferred): Use Discord's native message reference
        try:
            # Create a message reference to the original message
            message_reference = discord.MessageReference(
                message_id=message.id,
                channel_id=message.channel.id,
                guild_id=message.guild.id
            )
            
            # Create a string for the forwarded by info
            forwarder_info = f"Forwarded by {user.mention} from {message.channel.mention}"
            
            # Forward with native reference + informational text
            forward_msg = await notification_channel.send(
                content=forwarder_info,
                reference=message_reference,
                allowed_mentions=discord.AllowedMentions.none()
            )
            
            logger.info(f"Message from {message.author} forwarded to {notification_channel.name} by {user} using native reference")
            logger.info(f"Native reference data: message_id={message.id}, channel_id={message.channel.id}, guild_id={message.guild.id}")
            
            return
        except discord.errors.HTTPException as e:
            # If the native reference fails, log it and fall back to the webhook method
            logger.warning(f"Native message reference failed: {str(e)}. Falling back to webhook method.")
        
        # Fallback to webhook method if native reference fails
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
        
        # Send a note about who forwarded it and the message source
        source_info = ""
        if message.webhook_id:
            source_info = " (webhook message)"
        elif message.application_id:
            source_info = " (app message)"
            
        # Create an embed for the attribution info
        attribution_embed = discord.Embed(
            title="Message Forwarded",
            description=f"A message{source_info} was forwarded from: {message.channel.mention} by {user.mention}"
        )
        
        # Apply styling from embed_config
        from config import embed_config
        embed_config.apply_default_styling(attribution_embed)
        
        # Create a "Jump to Original" button
        view = discord.ui.View()
        button = discord.ui.Button(
            style=discord.ButtonStyle.link,
            label="Jump to Original Message",
            url=message.jump_url
        )
        view.add_item(button)
        
        # Send the styled embed with button
        await notification_channel.send(
            embed=attribution_embed,
            view=view,
            allowed_mentions=discord.AllowedMentions.none()
        )
        
        logger.info(f"Message from {message.author} forwarded to {notification_channel.name} by {user} using webhook method")
    except discord.errors.HTTPException as e:
        logger.error(f"Failed to forward message: {str(e)}")
        
        # Fallback mechanism if webhooks don't work
        try:
            # Use message.jump_url as a direct link to the original
            embed = discord.Embed(
                title="Forwarded Message",
                description=message.content,
                color=0x5865F2  # Discord blurple
            )
            
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
            
            # Determine source for content message
            source_info = ""
            if message.webhook_id:
                source_info = " (webhook message)"
            elif message.application_id:
                source_info = " (app message)"
                
            # Create an embed for the fallback attribution info
            attribution_embed = discord.Embed(
                title="Message Forwarded (Fallback Mode)",
                description=f"A message{source_info} was forwarded from: {message.channel.mention} by {user.mention}"
            )
            
            # Apply styling from embed_config
            embed_config.apply_default_styling(attribution_embed)
            
            # Create a "Jump to Original" button
            fallback_view = discord.ui.View()
            fallback_button = discord.ui.Button(
                style=discord.ButtonStyle.link,
                label="Jump to Original Message",
                url=message.jump_url
            )
            fallback_view.add_item(fallback_button)
            
            # Send the styled embed with button
            await notification_channel.send(
                embed=attribution_embed,
                view=fallback_view,
                allowed_mentions=discord.AllowedMentions.none()
            )
            
            # Send the original message content in an embed
            await notification_channel.send(
                embed=embed,
                allowed_mentions=discord.AllowedMentions.none()
            )
            
            # Handle attachments in fallback mode
            if message.attachments:
                for attachment in message.attachments:
                    try:
                        file = await attachment.to_file()
                        await notification_channel.send(file=file)
                    except:
                        await notification_channel.send(f"[Attachment: {attachment.filename}]({attachment.url})")
            
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
                    
                    await notification_channel.send(embed=embed)
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
    
    # Log the configuration
    logger.info(f"Reaction forward enabled: {config.ENABLED}")
    logger.info(f"Message forwarding enabled: {config.ENABLE_FORWARDING}")
    logger.info(f"Whitelisted categories: {config.CATEGORY_IDS}")
    logger.info(f"Blacklisted channels: {config.BLACKLIST_CHANNEL_IDS}")
    logger.info(f"Using notification channel ID: {pinger_config.NOTIFICATION_CHANNEL_ID}")
    
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