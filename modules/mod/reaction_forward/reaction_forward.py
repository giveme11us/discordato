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
        
        logger.info(f"Message from {message.author} forwarded to {notification_channel.name} by {user}")
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
                for embed in message.embeds:
                    await notification_channel.send(embed=embed)
            
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
    
    @bot.event
    async def on_message(message):
        # Process the message for the reaction_forward feature
        await process_message(message)
        
        # Make sure to call the bot's process_commands method
        # This ensures that other command processing still works
        await bot.process_commands(message)
    
    @bot.event
    async def on_reaction_add(reaction, user):
        # Process the reaction for forwarding messages
        await handle_reaction_add(reaction, user) 