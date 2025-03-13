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
from config import pinger_config, embed_config

logger = logging.getLogger('discord_bot.modules.mod.pinger')

async def process_message(message):
    """
    Process a message to check for @everyone or @here mentions.
    
    Args:
        message: The Discord message to process
    """
    # Add basic message information for debugging
    logger.debug(f"Processing message: content='{message.content}', author={message.author}, channel={message.channel.name}, guild={message.guild.name}")
    logger.debug(f"Message has mention_everyone={message.mention_everyone}, contains '@here'={'@here' in message.content}, role_mentions={len(message.role_mentions)}")
    
    # Skip if notification channel is not configured
    if not pinger_config.NOTIFICATION_CHANNEL_ID:
        logger.warning("Pinger notification channel not configured - PINGER_NOTIFICATION_CHANNEL_ID not set in .env")
        return
    
    logger.debug(f"Using notification channel ID: {pinger_config.NOTIFICATION_CHANNEL_ID}")
    
    # Skip messages from bots
    if message.author.bot:
        logger.debug(f"Skipping message from bot: {message.author}")
        return
    
    # Check if the message has any monitored mentions
    has_everyone = message.mention_everyone and pinger_config.MONITOR_EVERYONE
    has_here = "@here" in message.content and pinger_config.MONITOR_HERE
    has_role_mentions = len(message.role_mentions) > 0 and pinger_config.MONITOR_ROLES
    
    # Skip if message doesn't have any monitored mentions
    if not (has_everyone or has_here or has_role_mentions):
        logger.debug("Skipping message - no monitored mentions detected")
        logger.debug(f"Mention details: everyone={has_everyone}, here={has_here}, roles={has_role_mentions}")
        return
    
    logger.debug(f"Mention detected in message: mention_everyone={has_everyone}, contains @here={has_here}, role_mentions={has_role_mentions}")
    
    # Log user roles for debugging
    user_roles = [f"{role.name} (ID: {role.id})" for role in message.author.roles]
    logger.debug(f"User {message.author} has roles: {', '.join(user_roles)}")
    logger.debug(f"Whitelist role IDs: {pinger_config.WHITELIST_ROLE_IDS}")
    
    # Check if the user has a whitelisted role - only users with whitelisted roles can trigger notifications
    user_has_whitelisted_role = False
    for role in message.author.roles:
        if role.id in pinger_config.WHITELIST_ROLE_IDS:
            logger.debug(f"User {message.author} has whitelisted role {role.name} (ID: {role.id}), can trigger notifications")
            user_has_whitelisted_role = True
            break
    
    # If no whitelisted roles and whitelist is not empty, ignore this ping
    if not user_has_whitelisted_role and pinger_config.WHITELIST_ROLE_IDS:
        logger.debug(f"User {message.author} has no whitelisted roles, ignoring ping")
        return
    
    logger.debug(f"User {message.author} ping will trigger notification")
    
    # Determine which type of ping was used
    ping_type = None
    role_name = None
    
    if has_everyone:
        ping_type = "@everyone"
        logger.debug(f"Detected @everyone ping, MONITOR_EVERYONE={pinger_config.MONITOR_EVERYONE}")
    elif has_here:
        ping_type = "@here"
        logger.debug(f"Detected @here ping, MONITOR_HERE={pinger_config.MONITOR_HERE}")
    elif has_role_mentions:
        # Use the first role mention if there are multiple
        role = message.role_mentions[0]
        ping_type = f"@{role.name}"
        role_name = role.name
        logger.debug(f"Detected role ping: {ping_type}, MONITOR_ROLES={pinger_config.MONITOR_ROLES}")
    
    # If no monitored ping type was found, skip
    if not ping_type:
        logger.debug("Skipping - no monitored ping type detected")
        return
    
    logger.debug(f"Ping type detected: {ping_type}")
    
    # Get the notification channel
    notification_channel = message.guild.get_channel(pinger_config.NOTIFICATION_CHANNEL_ID)
    if not notification_channel:
        logger.warning(f"Could not find notification channel with ID {pinger_config.NOTIFICATION_CHANNEL_ID} in guild {message.guild.name} (ID: {message.guild.id})")
        
        # Log all available channels for debugging
        available_channels = [f"{channel.name} (ID: {channel.id})" for channel in message.guild.channels]
        logger.debug(f"Available channels in guild: {', '.join(available_channels)}")
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
    embed = discord.Embed(
        title=pinger_config.NOTIFICATION_TITLE,
    )
    
    # Add ping-specific fields
    embed.add_field(name="Role:", value=ping_type, inline=False)
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
    Set up the pinger feature.
    
    Args:
        bot: The Discord bot instance
    """
    logger.info("Setting up pinger feature")
    logger.info(f"Pinger configuration: notification_channel_id={pinger_config.NOTIFICATION_CHANNEL_ID}, whitelist_role_ids={pinger_config.WHITELIST_ROLE_IDS}")
    logger.info(f"Monitoring settings: monitor_everyone={pinger_config.MONITOR_EVERYONE}, monitor_here={pinger_config.MONITOR_HERE}")
    
    # Store a reference to the original on_message handler if it exists
    original_on_message = bot.event(bot.on_message) if hasattr(bot, 'on_message') else None
    logger.debug(f"Original on_message handler exists: {original_on_message is not None}")
    
    # Define a new on_message handler that combines our functionality with the original
    @bot.event
    async def on_message(message):
        try:
            # Process the message for pings
            logger.debug(f"Received message from {message.author}: '{message.content}'")
            await process_message(message)
        except Exception as e:
            logger.error(f"Error in pinger on_message handler: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Call the original handler if it exists
        if original_on_message:
            try:
                logger.debug("Calling original on_message handler")
                await original_on_message(message)
            except Exception as e:
                logger.error(f"Error in original on_message handler: {str(e)}")
        else:
            # If no original handler, at least process commands
            if not message.author.bot:
                try:
                    logger.debug("Processing commands")
                    await bot.process_commands(message)
                except Exception as e:
                    logger.error(f"Error processing commands: {str(e)}")
    
    logger.info("Pinger feature set up successfully")
    
    # Register help info
    if hasattr(bot, 'help_info'):
        bot.help_info['pinger'] = {
            'name': 'Pinger',
            'description': 'Monitors @everyone and @here mentions and sends notifications'
        } 