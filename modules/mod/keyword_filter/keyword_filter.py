"""
Keyword Filter Module

This module implements the keyword filtering functionality.
It scans messages for configured patterns and takes appropriate action.
"""

import re
import logging
import discord
import time
from collections import deque
from typing import Dict, List, Match, Optional, Tuple, Union
from discord.ext import commands
from config import keyword_filter_config as config
from config import embed_config
from utils import helpers

logger = logging.getLogger('discord_bot.modules.mod.keyword_filter')

# Add a deque to track recently processed messages (to avoid duplicates)
# Format: (message_id, timestamp)
recently_processed_messages = deque(maxlen=100)

def setup_keyword_filter(bot: commands.Bot) -> None:
    """
    Set up the keyword filter module.
    
    Args:
        bot: The Discord bot instance
    """
    # Get values directly from settings_manager
    enabled = config.settings_manager.get("ENABLED", False)
    dry_run = config.settings_manager.get("DRY_RUN", True)
    category_ids = config.settings_manager.get("CATEGORY_IDS", [])
    monitor_channel_ids = config.settings_manager.get("MONITOR_CHANNEL_IDS", [])
    blacklist_channel_ids = config.settings_manager.get("BLACKLIST_CHANNEL_IDS", [])
    notification_channel_id = config.settings_manager.get("NOTIFICATION_CHANNEL_ID")
    filters = config.settings_manager.get("FILTERS", {})
    
    if not enabled:
        logger.info("Keyword filter module is disabled.")
        return

    logger.info(f"Setting up keyword filter module (Dry Run: {dry_run})")
    logger.info(f"Category IDs: {category_ids}")
    logger.info(f"Monitored Channel IDs: {monitor_channel_ids}")
    logger.info(f"Blacklisted Channel IDs: {blacklist_channel_ids}")
    logger.info(f"Notification Channel ID: {notification_channel_id}")
    
    # Log active filters
    active_filters = [name for name, settings in filters.items() if settings.get('enabled', False)]
    logger.info(f"Active filters: {', '.join(active_filters) if active_filters else 'None'}")
    
    # Check if the bot already has an on_message handler (likely set up in discord_bot.py)
    original_on_message = None
    if hasattr(bot, 'event_handlers') and 'on_message' in bot.event_handlers:
        logger.info("Main on_message handler already exists, not registering a duplicate")
        # Store a reference to process_message for the main handler to use instead
        bot.keyword_filter_process = process_message
    else:
        # Only register our own handler if no main handler exists
        @bot.event
        async def on_message(message: discord.Message) -> None:
            """
            Event handler for messages.
            
            Args:
                message: The message to process
            """
            # Process webhook messages, but ignore regular bot messages
            if message.author.bot and not message.webhook_id:
                logger.debug(f"Skipping message from bot: {message.author}")
                return

            # Process the message through keyword filters
            await process_message(bot, message)
            
            # Continue command processing
            await bot.process_commands(message)
    
    logger.info("Keyword filter module set up successfully.")

async def process_message(bot: commands.Bot, message: discord.Message) -> None:
    """
    Process a message through the keyword filter.
    
    Args:
        bot: The Discord bot instance
        message: The message to process
    """
    # Check if we've already processed this message recently
    if any(msg_id == message.id for msg_id, _ in recently_processed_messages):
        logger.debug(f"Skipping already processed message: {message.id}")
        return
        
    # Add this message to our recently processed list
    recently_processed_messages.append((message.id, time.time()))
    
    # Get values directly from settings_manager
    enabled = config.settings_manager.get("ENABLED", False)
    rules = config.settings_manager.get("RULES", {})
    notification_channel_id = config.settings_manager.get("NOTIFICATION_CHANNEL_ID")
    
    # Skip processing if the module is disabled
    if not enabled:
        return
    
    # Skip processing if this is our own message in a notification channel 
    # This prevents message forwarding loops - IMPORTANT!
    if message.author.id == bot.user.id:
        # Check if this is a notification channel
        if message.channel.id == notification_channel_id:
            logger.debug(f"Skipping our own message in notification channel")
            return
        
        # Check if this channel is a rule-specific notification channel
        for rule_id, rule in rules.items():
            if rule.get('alert_channel_id') == message.channel.id:
                logger.debug(f"Skipping our own message in rule-specific notification channel")
                return
    
    # Get some basic message info for logging
    is_webhook = message.webhook_id is not None
    is_bot = message.author.bot
    channel_name = getattr(message.channel, 'name', 'Unknown')
    category_name = getattr(message.channel.category, 'name', 'None') if hasattr(message.channel, 'category') else 'None'
    
    # Get channel and category information
    category_id = message.channel.category_id if hasattr(message.channel, 'category_id') else None
    channel_id = message.channel.id
    
    # Collect all text content to check (message content + embed content)
    all_content = []
    
    # Extra logging for webhook messages
    if is_webhook:
        logger.info(f"Processing webhook message in {channel_name} (category: {category_name}) from {message.author}")
    
    # Always include message content if it exists
    if message.content:
        all_content.append(message.content)
        logger.debug(f"Message content: {message.content[:100]}{'...' if len(message.content) > 100 else ''}")
    
    # Extract text from embeds - extra careful with webhooks/bots
    if message.embeds:
        logger.debug(f"Message has {len(message.embeds)} embeds")
        
        for i, embed in enumerate(message.embeds):
            embed_texts = []
            
            if embed.title:
                embed_texts.append(embed.title)
                all_content.append(embed.title)
                logger.debug(f"Embed {i+1} title: {embed.title}")
                
            if embed.description:
                embed_texts.append(embed.description)
                all_content.append(embed.description)
                logger.debug(f"Embed {i+1} description: {embed.description}")
                
            # Process fields
            for j, field in enumerate(embed.fields):
                if field.name:
                    embed_texts.append(field.name)
                    all_content.append(field.name)
                    logger.debug(f"Embed {i+1} field {j+1} name: {field.name}")
                if field.value:
                    embed_texts.append(field.value)
                    all_content.append(field.value)
                    logger.debug(f"Embed {i+1} field {j+1} value: {field.value[:100]}{'...' if len(field.value) > 100 else ''}")
            
            # Add footer if present
            if embed.footer and embed.footer.text:
                embed_texts.append(embed.footer.text)
                all_content.append(embed.footer.text)
                logger.debug(f"Embed {i+1} footer: {embed.footer.text}")
            
            # Add author if present
            if embed.author and embed.author.name:
                embed_texts.append(embed.author.name)
                all_content.append(embed.author.name)
                logger.debug(f"Embed {i+1} author: {embed.author.name}")
            
            # Log the combined embed content for this embed
            combined_embed = "\n".join(embed_texts)
            logger.debug(f"Combined embed {i+1} content: {combined_embed[:300]}{'...' if len(combined_embed) > 300 else ''}")
    
    # Combine all content for a comprehensive check
    combined_content = "\n".join(all_content)
    if not combined_content.strip():
        logger.debug("Skipping message - no content to check")
        return
    
    # Check message against all rules - track matches by rule
    matched_by_rule = {}
    
    # Check each active rule
    for rule_id, rule in rules.items():
        # Skip disabled rules
        if not rule.get('enabled', True):
            continue
        
        # Check if we should monitor this channel
        should_monitor = False
        
        # Check if channel is in rule's category list
        rule_categories = rule.get('category_ids', [])
        if category_id and category_id in rule_categories:
            should_monitor = True
            logger.debug(f"Channel matches category filter for rule '{rule_id}'")
            
        # Check if channel is directly monitored by rule
        rule_channels = rule.get('channel_ids', [])
        if channel_id in rule_channels:
            should_monitor = True
            logger.debug(f"Channel is directly monitored by rule '{rule_id}'")
            
        # Check if channel is blacklisted by rule
        rule_blacklist = rule.get('blacklist_ids', [])
        if channel_id in rule_blacklist:
            logger.debug(f"Channel is blacklisted by rule '{rule_id}'")
            should_monitor = False
            
        # Skip rule if we shouldn't monitor this channel
        if not should_monitor:
            continue
        
        # Get keywords for this rule
        keywords = rule.get('keywords', [])
        if not keywords:
            continue
            
        # Check for keyword matches
        matches = []
        for keyword in keywords:
            # Skip empty keywords
            if not keyword.strip():
                continue
                
            # Do a simple case-insensitive check
            keyword_lower = keyword.lower()
            content_lower = combined_content.lower()
            
            # Check if it's a regex pattern
            is_regex = any(c in keyword for c in '[]()\\.*+?{}|^$')
            
            if is_regex:
                # Try regex matching
                try:
                    for match in re.finditer(keyword, combined_content, re.IGNORECASE):
                        matches.append({
                            'pattern': keyword,
                            'matched_text': match.group(0),
                            'start': match.start(),
                            'end': match.end()
                        })
                except re.error as e:
                    logger.error(f"Invalid regex pattern '{keyword}': {e}")
            else:
                # Do simple substring matching
                start_pos = 0
                while True:
                    found_pos = content_lower.find(keyword_lower, start_pos)
                    if found_pos == -1:
                        break
                        
                    # Found a match
                    matched_text = combined_content[found_pos:found_pos + len(keyword)]
                    matches.append({
                        'pattern': keyword,
                        'matched_text': matched_text,
                        'start': found_pos,
                        'end': found_pos + len(keyword)
                    })
                    start_pos = found_pos + 1
        
        # If we found matches, store them with the rule
        if matches:
            logger.warning(
                f"Rule '{rule_id}' matched message from {message.author} in #{channel_name}: "
                f"{combined_content[:100]}{'...' if len(combined_content) > 100 else ''}"
            )
            
            # Log each keyword that matched
            for match in matches:
                logger.warning(f"  - Matched keyword '{match['pattern']}' with text: {match['matched_text']}")
                
            # Store with rule info
            rule_info = {
                'matches': matches,
                'action': rule.get('action', 'notify'),
                'severity': rule.get('severity', 'medium'),
                'alert_channel_id': rule.get('alert_channel_id'),
                'name': rule.get('name', rule_id)
            }
            
            matched_by_rule[rule_id] = rule_info
    
    # Process all matched rules
    if matched_by_rule:
        logger.info(f"Message matched {len(matched_by_rule)} rules")
        await handle_matched_rules(bot, message, matched_by_rule)
    else:
        logger.debug("No rules matched for this message")

def check_filter_match(content: str, filter_config: Dict[str, Union[bool, List[str], str]]) -> Optional[Dict]:
    """
    Check if message content matches a filter.
    
    Args:
        content: Message content
        filter_config: Filter configuration
        
    Returns:
        Dict with match information or None if no match
    """
    if not content or not filter_config.get('enabled', False):
        return None
    
    patterns = filter_config.get('patterns', [])
    if not patterns:
        return None
    
    matches = []
    
    # First, try simple case-insensitive literal match for performance and reliability
    # This works especially well for embeds and webhook messages
    for pattern in patterns:
        # If pattern looks like a regex (has special chars), skip this step
        if any(c in pattern for c in '[]()\\.*+?{}|^$'):
            continue
            
        # Do a simple case-insensitive check first
        pattern_lower = pattern.lower()
        content_lower = content.lower()
        
        start_pos = 0
        while True:
            found_pos = content_lower.find(pattern_lower, start_pos)
            if found_pos == -1:
                break
                
            # Found a match
            matched_text = content[found_pos:found_pos + len(pattern)]
            matches.append({
                'pattern': pattern,
                'matched_text': matched_text,
                'start': found_pos,
                'end': found_pos + len(pattern)
            })
            start_pos = found_pos + 1
    
    # Then try regex patterns for more complex matching
    for pattern in patterns:
        try:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                # Check if this match overlaps with any existing matches - skip if so
                match_start = match.start()
                match_end = match.end()
                overlap = False
                
                for existing_match in matches:
                    if (match_start <= existing_match['end'] and 
                        match_end >= existing_match['start']):
                        overlap = True
                        break
                
                if not overlap:
                    matches.append({
                        'pattern': pattern,
                        'matched_text': match.group(0),
                        'start': match_start,
                        'end': match_end
                    })
        except re.error as e:
            logger.error(f"Invalid regex pattern '{pattern}': {e}")
    
    return {
        'matches': matches,
        'description': filter_config.get('description', 'No description'),
        'action': filter_config.get('action', 'log'),
        'severity': filter_config.get('severity', 'medium')
    } if matches else None

async def handle_matched_rules(
    bot: commands.Bot, 
    message: discord.Message, 
    matched_rules: Dict[str, Dict]
) -> None:
    """
    Handle matched rules by taking appropriate actions.
    
    Args:
        bot: The Discord bot instance
        message: The message that matched rules
        matched_rules: Dictionary of matched rules with their results
    """
    # Get values directly from settings_manager
    dry_run = config.settings_manager.get("DRY_RUN", True)
    default_notification_channel_id = config.settings_manager.get("NOTIFICATION_CHANNEL_ID")
    notify_filtered = config.settings_manager.get("NOTIFY_FILTERED", True)
    
    # FIXED: Only skip if the message is from our bot *AND* in a notification channel
    # (Not just any message in a notification channel)
    if message.author.id == bot.user.id and message.channel.id == default_notification_channel_id:
        logger.debug(f"Skipping processing for our own message {message.id} in notification channel")
        return
        
    # Group rules by their alert channels for more efficient processing
    rules_by_channel = {}
    
    # Determine the highest severity action across all matched rules
    action_priorities = {'log': 1, 'notify': 2, 'delete': 3}
    highest_action = 'log'
    highest_severity = 'low'
    
    for rule_id, rule_data in matched_rules.items():
        action = rule_data['action']
        severity = rule_data['severity']
        
        # Update highest action if this one has higher priority
        if action_priorities.get(action, 0) > action_priorities.get(highest_action, 0):
            highest_action = action
        
        # Update highest severity
        severity_levels = {'low': 1, 'medium': 2, 'high': 3}
        if severity_levels.get(severity, 0) > severity_levels.get(highest_severity, 0):
            highest_severity = severity
            
        # Group this rule with its alert channel
        alert_channel_id = rule_data.get('alert_channel_id')
        # If no rule-specific alert channel, use the default
        if not alert_channel_id:
            alert_channel_id = default_notification_channel_id
            
        if alert_channel_id not in rules_by_channel:
            rules_by_channel[alert_channel_id] = {}
            
        rules_by_channel[alert_channel_id][rule_id] = rule_data
    
    logger.debug(f"Sending alerts to {len(rules_by_channel)} channels for message {message.id}")
    
    # Process forwarding for each alert channel group
    alerts_sent = False
    for alert_channel_id, channel_rules in rules_by_channel.items():
        if not alert_channel_id:
            logger.debug(f"No alert channel specified for rules: {list(channel_rules.keys())}")
            continue  # Skip if no alert channel
            
        # Skip if this is our own message and already in the alert channel
        if message.author.id == bot.user.id and message.channel.id == alert_channel_id:
            logger.debug(f"Skipping alert to channel {alert_channel_id} - message already there")
            continue
            
        notification_channel = bot.get_channel(alert_channel_id)
        if notification_channel:
            # Forward message to this channel with these rules
            await forward_message(bot, message, notification_channel, channel_rules)
            logger.info(f"Forwarded message {message.id} from {message.author} to {notification_channel.name} for {len(channel_rules)} rule(s)")
            alerts_sent = True
        else:
            logger.error(f"Could not find notification channel with ID {alert_channel_id}")
    
    # Take delete action based on configuration if any rule requires it
    should_delete = highest_action == 'delete' and not dry_run
    if should_delete:
        try:
            await message.delete()
            logger.info(f"Deleted message from {message.author} due to rule matches")
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
    
    # Send notification if configured AND we didn't forward to any channel
    # This ensures we either forward the original message OR send a notification, but not both
    if notify_filtered and not alerts_sent and (highest_action in ['notify', 'delete'] or dry_run):
        await send_notification(bot, message, matched_rules, highest_severity)

async def forward_message(
    bot: commands.Bot,
    message: discord.Message, 
    destination_channel: discord.TextChannel,
    matched_rules: Dict[str, Dict]
) -> None:
    """
    Forward a message to the destination channel.
    
    Args:
        bot: The Discord bot instance
        message: The message to forward
        destination_channel: The channel to forward the message to
        matched_rules: Dictionary of matched rules with their results
    """
    # Safety check - don't forward messages that are already in the destination channel
    if message.channel.id == destination_channel.id:
        logger.debug(f"Skipping forward - message already in destination channel {destination_channel.id}")
        return
        
    # Safety check - only skip our own messages if they're in a notification channel
    # This prevents only actual loops, not legitimate forwards
    if message.author.id == bot.user.id and any(channel_id == message.channel.id for channel_id in [
        config.settings_manager.get("NOTIFICATION_CHANNEL_ID"),
        # Check for rule-specific alert channels
        *[rule.get('alert_channel_id') for rule in config.settings_manager.get("RULES", {}).values() if rule.get('alert_channel_id')]
    ]):
        logger.debug(f"Skipping forward - message is from our bot in a notification channel")
        return
    
    # Attempt to forward the message content
    try:
        # If there's message content, forward it
        if message.content:
            # If the content is too long, split it
            if len(message.content) > 2000:
                parts = [message.content[i:i+1990] for i in range(0, len(message.content), 1990)]
                for i, part in enumerate(parts):
                    await destination_channel.send(f"{part}" + (f" (continued {i+1}/{len(parts)})" if len(parts) > 1 else ""))
            else:
                await destination_channel.send(message.content)
        
        # Handle attachments
        for attachment in message.attachments:
            try:
                # For images and small files, just re-upload them
                if attachment.size < 8388608 and attachment.filename:  # 8MB limit
                    file = await attachment.to_file()
                    await destination_channel.send(file=file)
                else:
                    # For larger files, just send the URL
                    await destination_channel.send(f"Attachment (too large to forward): {attachment.url}")
            except Exception as e:
                logger.error(f"Failed to forward attachment: {e}")
                await destination_channel.send(f"Failed to forward attachment: {attachment.url}")
        
        # Handle embeds by creating new ones with the same content
        for embed in message.embeds:
            try:
                # Clone the embed for forwarding
                new_embed = discord.Embed()
                
                # Copy basic embed properties
                if embed.title:
                    new_embed.title = embed.title
                if embed.description:
                    new_embed.description = embed.description
                if embed.url:
                    new_embed.url = embed.url
                
                # Copy author if present
                if embed.author:
                    author_name = embed.author.name
                    author_url = embed.author.url
                    author_icon_url = embed.author.icon_url
                    new_embed.set_author(
                        name=author_name,
                        url=author_url,
                        icon_url=author_icon_url
                    )
                
                # Copy color
                if embed.color:
                    new_embed.color = embed.color
                
                # Copy footer
                if embed.footer:
                    footer_text = embed.footer.text
                    footer_icon_url = embed.footer.icon_url
                    new_embed.set_footer(
                        text=footer_text,
                        icon_url=footer_icon_url
                    )
                
                # Copy thumbnail
                if embed.thumbnail and embed.thumbnail.url:
                    new_embed.set_thumbnail(url=embed.thumbnail.url)
                
                # Copy image
                if embed.image and embed.image.url:
                    new_embed.set_image(url=embed.image.url)
                
                # Copy timestamp
                if embed.timestamp:
                    new_embed.timestamp = embed.timestamp
                
                # Copy fields
                for field in embed.fields:
                    new_embed.add_field(
                        name=field.name,
                        value=field.value,
                        inline=field.inline
                    )
                
                # No longer apply default styling - preserve original embed appearance
                # new_embed = embed_config.apply_default_styling(new_embed)
                
                await destination_channel.send(embed=new_embed)
            except Exception as e:
                logger.error(f"Error forwarding embed: {e}")
                # If we can't recreate the embed, at least try to send the textual content
                content = []
                if embed.title:
                    content.append(f"**Embed Title**: {embed.title}")
                if embed.description:
                    content.append(f"**Embed Description**: {embed.description}")
                for field in embed.fields:
                    content.append(f"**{field.name}**: {field.value}")
                
                if content:
                    await destination_channel.send("\n".join(content)[:2000])
                else:
                    await destination_channel.send("*[Could not forward embed content]*")
        
        # If there was no content, embeds, or attachments, send a placeholder message
        if not message.content and not message.embeds and not message.attachments:
            await destination_channel.send("*[Empty message or unsupported content]*")
        
    except Exception as e:
        logger.error(f"Failed to forward message: {e}")
        await destination_channel.send(f"Error forwarding message: {str(e)[:1900]}")

async def send_notification(
    bot: commands.Bot, 
    message: discord.Message, 
    matched_rules: Dict[str, Dict],
    severity: str
) -> None:
    """
    Send notification about a filtered message.
    
    Args:
        bot: The Discord bot instance
        message: The message that matched rules
        matched_rules: Dictionary of matched rules with their results
        severity: The highest severity level
    """
    # Get values directly from settings_manager
    notification_channel_id = config.settings_manager.get("NOTIFICATION_CHANNEL_ID")
    dry_run = config.settings_manager.get("DRY_RUN", True)
    
    if not notification_channel_id:
        logger.warning("No notification channel configured for keyword filter")
        return
    
    # Get the notification channel
    notification_channel = bot.get_channel(notification_channel_id)
    if not notification_channel:
        logger.error(f"Could not find notification channel with ID {notification_channel_id}")
        return
    
    # Create the notification embed
    color_map = {'low': discord.Color.green(), 'medium': discord.Color.gold(), 'high': discord.Color.red()}
    
    is_webhook = message.webhook_id is not None
    is_bot = message.author.bot
    
    # Use a more attention-grabbing title if the match came from a webhook/bot
    if is_webhook or is_bot:
        title = "⚠️ Webhook/Bot Message Filter Alert"
    else:
        title = "Message Filter Alert"
    
    embed = discord.Embed(
        title=title,
        description=f"A message matched filter criteria in {message.channel.mention}",
        color=color_map.get(severity, discord.Color.gold())
    )
    
    # Add author information with webhook/bot status
    author_info = f"{message.author.mention} ({message.author})"
    if is_webhook:
        author_info += " [Webhook]"
    elif is_bot:
        author_info += " [Bot]"
        
    embed.add_field(name="Author", value=author_info, inline=True)
    embed.add_field(name="Channel", value=message.channel.mention, inline=True)
    embed.add_field(name="Timestamp", value=f"<t:{int(message.created_at.timestamp())}:F>", inline=True)
    
    # Add matched rule information
    rules_info = []
    for rule_id, rule_data in matched_rules.items():
        matches = rule_data['matches']
        matched_texts = [m.get('matched_text', 'Unknown') for m in matches]
        
        rule_text = f"**{rule_data['name']}** ({rule_data['severity']}):\n"
        rule_text += f"Matched: {', '.join(f'`{text}`' for text in matched_texts[:3])}"
        rule_text += f"{'... and more' if len(matched_texts) > 3 else ''}"
        
        rules_info.append(rule_text)
    
    embed.add_field(name="Matched Rules", value="\n".join(rules_info), inline=False)
    
    # Add message content
    content = message.content
    if content:
        if len(content) > 1024:
            content = content[:1021] + "..."
        embed.add_field(name="Message Content", value=content, inline=False)
    else:
        embed.add_field(name="Message Content", value="(No text content)", inline=False)
    
    # Add embed information if present
    if message.embeds:
        embed_info = []
        for i, msg_embed in enumerate(message.embeds):
            embed_parts = []
            embed_matched = False
            
            for rule_id, rule_data in matched_rules.items():
                for match in rule_data['matches']:
                    matched_text = match.get('matched_text', '').lower()
                    
                    # Check if this match could be in the embed title
                    if msg_embed.title and matched_text in msg_embed.title.lower():
                        embed_matched = True
                        embed_parts.append(f"**Title**: {msg_embed.title} ⟵ __MATCHED__")
                    elif msg_embed.title:
                        embed_parts.append(f"**Title**: {msg_embed.title}")
                    
                    # Check if match could be in embed description
                    if msg_embed.description:
                        if matched_text in msg_embed.description.lower():
                            embed_matched = True
                            # Highlight the matched part in the description
                            desc = msg_embed.description
                            if len(desc) > 300:
                                desc = desc[:297] + "..."
                            embed_parts.append(f"**Description**: {desc} ⟵ __MATCHED__")
                        else:
                            desc = msg_embed.description
                            if len(desc) > 300:
                                desc = desc[:297] + "..."
                            embed_parts.append(f"**Description**: {desc}")
            
            # If we didn't find matches in title/description specifically, just show normal embed
            if not embed_parts:
                if msg_embed.title:
                    embed_parts.append(f"**Title**: {msg_embed.title}")
                if msg_embed.description:
                    desc = msg_embed.description
                    if len(desc) > 300:
                        desc = desc[:297] + "..."
                    embed_parts.append(f"**Description**: {desc}")
            
            # Add fields note if present
            if msg_embed.fields:
                embed_parts.append(f"**Fields**: {len(msg_embed.fields)} fields" + 
                                  (" ⟵ __MATCHED__ (keyword found in fields)" if embed_matched and not embed_parts else ""))
            
            if embed_parts:
                embed_header = f"**Embed {i+1}:**" + (" ⟵ __CONTAINS MATCHED CONTENT__" if embed_matched else "")
                embed_info.append(f"{embed_header}\n" + "\n".join(embed_parts))
        
        if embed_info:
            combined_info = "\n\n".join(embed_info)
            if len(combined_info) > 1024:
                combined_info = combined_info[:1021] + "..."
            embed.add_field(name="Embed Content", value=combined_info, inline=False)
    
    # Add action taken
    if dry_run:
        action = "Logged only (Dry Run mode)"
    else:
        action = "Message was deleted" if any(rule_data['action'] == 'delete' for rule_data in matched_rules.values()) else "Message was logged"
    
    embed.add_field(name="Action Taken", value=action, inline=False)
    
    # Add message ID and link
    embed.add_field(name="Message ID", value=message.id, inline=True)
    embed.add_field(name="Jump to Message", value=f"[Click Here]({message.jump_url})", inline=True)
    
    # Apply default styling
    embed = embed_config.apply_default_styling(embed)
    
    # Send the notification
    try:
        await notification_channel.send(embed=embed)
        logger.info(f"Sent keyword filter notification to channel {notification_channel.name}")
    except Exception as e:
        logger.error(f"Failed to send keyword filter notification: {e}") 