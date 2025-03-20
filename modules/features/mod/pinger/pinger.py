"""
Pinger Feature

This module monitors messages for @everyone and @here mentions
and sends notifications to a dedicated channel.
Only users with roles in the whitelist can trigger notifications.
"""

import logging
import discord
from discord import app_commands
from discord.ui import Button, View
from config.features.pinger_config import pinger_config
from config.features import embed_config

logger = logging.getLogger('discord_bot.modules.mod.pinger')

async def process_message(message):
    """
    Process a message to check for @everyone or @here mentions.
    
    Args:
        message: The Discord message to process
    """
    # Add basic message information for debugging
    try:
        # Check if the message is in a guild or DM channel
        if message.guild:
            channel_info = message.channel.name
            guild_info = message.guild.name
        else:
            channel_info = "DM Channel"
            guild_info = "Direct Message"
            
        logger.debug(f"Processing message: content='{message.content}', author={message.author}, channel={channel_info}, guild={guild_info}")
        logger.debug(f"Message has mention_everyone={message.mention_everyone}, contains '@here'={'@here' in message.content}, role_mentions={len(message.role_mentions)}")
    except Exception as e:
        logger.debug(f"Error logging message info: {str(e)}")
    
    # Get current configuration values directly from properties
    notification_channel_id = pinger_config.NOTIFICATION_CHANNEL_ID
    monitor_everyone = pinger_config.MONITOR_EVERYONE
    monitor_here = pinger_config.MONITOR_HERE
    monitor_roles = pinger_config.MONITOR_ROLES
    whitelist_role_ids = pinger_config.WHITELIST_ROLE_IDS
    
    # Skip if notification channel is not configured
    if not notification_channel_id:
        logger.warning("Pinger notification channel not configured - PINGER_NOTIFICATION_CHANNEL_ID not set in .env")
        return
    
    logger.debug(f"Using notification channel ID: {notification_channel_id}")
    
    # Skip messages from bots
    if message.author.bot:
        logger.debug(f"Skipping message from bot: {message.author}")
        return
    
    # Skip direct messages
    if not message.guild:
        logger.debug("Skipping direct message")
        return
    
    # Check for monitored mentions
    has_everyone = message.mention_everyone and monitor_everyone
    has_here = "@here" in message.content and monitor_here
    has_role_mentions = len(message.role_mentions) > 0 and monitor_roles
    
    if not (has_everyone or has_here or has_role_mentions):
        logger.debug("Skipping message - no monitored mentions detected")
        logger.debug(f"Mention details: everyone={has_everyone}, here={has_here}, roles={has_role_mentions}")
        return
    
    # Check if user has a whitelisted role (if whitelist is enabled)
    user_has_whitelisted_role = False
    
    # Log whitelist for debugging
    logger.debug(f"Whitelist role IDs: {whitelist_role_ids}")
    
    # Check each of the user's roles
    for role in message.author.roles:
        if role.id in whitelist_role_ids:
            user_has_whitelisted_role = True
            logger.debug(f"User {message.author} has whitelisted role {role.name}")
            break
    
    # Skip if whitelist is enabled and user doesn't have a whitelisted role
    if not user_has_whitelisted_role and whitelist_role_ids:
        logger.debug(f"User {message.author} has no whitelisted roles, ignoring ping")
        return
    
    logger.debug(f"User {message.author} ping will trigger notification")
    
    # Get details on what was mentioned
    ping_type = ""
    ping_target = ""
    if has_everyone:
        ping_type = "@everyone"
        ping_target = "server members"
        logger.debug(f"Detected @everyone ping, MONITOR_EVERYONE={monitor_everyone}")
    elif has_here:
        ping_type = "@here"
        ping_target = "online members"
        logger.debug(f"Detected @here ping, MONITOR_HERE={monitor_here}")
    elif has_role_mentions:
        role_names = [role.name for role in message.role_mentions]
        ping_type = f"@{role_names[0]}" if len(role_names) == 1 else f"@{role_names[0]} +{len(role_names)-1}"
        ping_target = ", ".join([f"@{role.name}" for role in message.role_mentions[:3]])
        if len(message.role_mentions) > 3:
            ping_target += f" +{len(message.role_mentions) - 3} more"
        logger.debug(f"Detected role ping: {ping_type}, MONITOR_ROLES={monitor_roles}")
    
    # Find out which channel to notify in
    notification_channel = None
    try:
        # Get the notification channel
        notification_channel = message.guild.get_channel(notification_channel_id)
        if not notification_channel:
            logger.warning(f"Could not find notification channel with ID {notification_channel_id} in guild {message.guild.name} (ID: {message.guild.id})")
            return
    except Exception as e:
        logger.error(f"Error while getting notification channel: {str(e)}")
        return
    
    logger.debug(f"Found notification channel: {notification_channel.name} (ID: {notification_channel.id})")
    
    # Create the embed for the notification
    logger.debug(f"Creating ping notification embed for {ping_type} ping")
    embed = create_ping_notification_embed(message, ping_type)
    
    # Create the Jump to Ping button
    logger.debug(f"Creating Jump to Ping button with URL: {message.jump_url}")
    view = create_jump_button(message)
    
    # Send the notification
    try:
        logger.debug(f"Attempting to send notification to channel {notification_channel.name}")
        await notification_channel.send(embed=embed, view=view)
        logger.info(f"Sent ping notification for {ping_type} ping by {message.author} in {message.channel.name}")
    except Exception as e:
        logger.error(f"Error sending ping notification: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Channel permissions: {notification_channel.permissions_for(message.guild.me)}")

def create_ping_notification_embed(message, ping_type):
    """
    Create an embed for the ping notification.
    
    Args:
        message: The Discord message containing the ping
        ping_type: The type of ping (@everyone or @here)
    
    Returns:
        discord.Embed: The notification embed
    """
    # Get title directly from property
    notification_title = "IMPORTANT PING"  # Using default value since we don't have this in config
    
    embed = discord.Embed(
        title=notification_title,
    )
    
    # Add channel field only (removing the Role field)
    embed.add_field(name="Channel:", value=f"<#{message.channel.id}>", inline=False)
    
    # Set timestamp from the message
    embed.timestamp = message.created_at
    
    # Apply default styling from global embed config
    return embed_config.apply_default_styling(embed)

def create_jump_button(message):
    """
    Create a view with a Jump to Ping button.
    
    Args:
        message: The Discord message to link to
    
    Returns:
        discord.ui.View: A view containing the jump button
    """
    view = View(timeout=None)  # Button never expires
    
    # Create a button that links to the message
    button = Button(
        style=discord.ButtonStyle.link,
        label="Jump to Ping",
        url=message.jump_url
    )
    
    view.add_item(button)
    return view

def setup_pinger(bot):
    """
    Set up the pinger feature for a bot.
    
    Args:
        bot: The Discord bot to set up
    """
    logger.info("Setting up pinger feature")
    
    # Get configuration values directly from properties
    notification_channel_id = pinger_config.NOTIFICATION_CHANNEL_ID
    whitelist_role_ids = pinger_config.WHITELIST_ROLE_IDS
    monitor_everyone = pinger_config.MONITOR_EVERYONE
    monitor_here = pinger_config.MONITOR_HERE
    monitor_roles = pinger_config.MONITOR_ROLES
    
    # Log the configuration
    logger.info(f"Pinger configuration: notification_channel_id={notification_channel_id}, whitelist_role_ids={whitelist_role_ids}")
    logger.info(f"Monitoring settings: monitor_everyone={monitor_everyone}, monitor_here={monitor_here}, monitor_roles={monitor_roles}")
    
    # Store the original on_message handler if it exists
    original_on_message = getattr(bot, 'on_message', None)
    logger.debug(f"Original on_message handler exists: {original_on_message is not None}")
    
    # Listen for messages to detect mentions
    @bot.listen('on_message')
    async def on_message_pinger(message):
        """
        Listen for messages with mentions and send notifications.
        
        Args:
            message: The Discord message to process
        """
        try:
            # Process the message for mentions
            await process_message(message)
        except Exception as e:
            logger.error(f"Error in pinger on_message handler: {str(e)}")
            import traceback
            logger.error(f"Exception traceback: {traceback.format_exc()}")
        
        # Call the original handler if it exists
        try:
            if original_on_message:
                logger.debug("Calling original on_message handler")
                await original_on_message(message)
        except Exception as e:
            logger.error(f"Error in original on_message handler: {str(e)}")
    
    logger.info("Pinger feature set up successfully")
    
    # Register help info
    if hasattr(bot, 'help_info'):
        bot.help_info['pinger'] = {
            'name': 'Pinger',
            'description': 'Monitors @everyone and @here mentions and sends notifications'
        } 