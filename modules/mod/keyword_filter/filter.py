"""
Keyword Filter Implementation

This module implements the functionality for filtering messages based on keywords.
"""

import discord
import logging
import re
from typing import Dict, List, Optional, Tuple, Union
from config import keyword_filter_config as config
from config.settings_manager import get_manager
from config import embed_config

logger = logging.getLogger('discord_bot.modules.mod.keyword_filter.filter')

async def process_message(message: discord.Message) -> None:
    """
    Process a message to check for keyword matches.
    
    Args:
        message: The Discord message to process
    """
    # Skip processing if the module is disabled
    if not config.ENABLED:
        return
    
    # Get some basic message info for logging
    is_webhook = message.webhook_id is not None
    is_bot = message.author.bot
    channel_name = getattr(message.channel, 'name', 'Unknown')
    category_name = getattr(message.channel.category, 'name', 'None') if hasattr(message.channel, 'category') else 'None'
    
    # Extra logging for webhook messages
    if is_webhook:
        logger.info(f"Processing webhook message in {channel_name} (category: {category_name}) from {message.author}")
    
    # Check if the message is in a monitored category
    category_id = message.channel.category_id if hasattr(message.channel, 'category_id') else None
    
    # Debug the category check
    logger.debug(f"Message category_id: {category_id}, Monitored categories: {config.CATEGORY_IDS}")
    logger.debug(f"Channel ID: {message.channel.id}, Blacklisted channels: {config.BLACKLIST_CHANNEL_IDS}")
    
    # Skip if the message is not in a monitored category or is in a blacklisted channel
    if (not category_id or category_id not in config.CATEGORY_IDS or 
        message.channel.id in config.BLACKLIST_CHANNEL_IDS):
        if is_webhook:
            logger.info(f"Skipping webhook message - not in monitored category or in blacklisted channel")
        return
    
    # Get channel and author information for logging
    author_name = str(message.author)
    
    logger.debug(f"Processing message in #{channel_name} from {author_name} (webhook: {is_webhook}, bot: {is_bot})")
    
    # Collect all text content to check (message content + embed content)
    all_content = []
    
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
                logger.debug(f"Embed {i+1} description: {embed.description[:100]}{'...' if len(embed.description) > 100 else ''}")
                
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
    
    # Combine all content for a comprehensive check
    combined_content = "\n".join(all_content)
    if not combined_content.strip():
        logger.debug("Skipping message - no content to check")
        return
    
    logger.debug(f"Combined content to check: {combined_content[:300]}{'...' if len(combined_content) > 300 else ''}")
    
    # Check message against all enabled filters
    matched_filters = []
    for filter_name, filter_config in config.FILTERS.items():
        if not filter_config.get('enabled', False):
            continue
        
        logger.debug(f"Checking filter: {filter_name}")
        filter_result = check_filter_match(combined_content, filter_config)
        if filter_result and filter_result['matches']:
            matched_filters.append((filter_name, filter_result))
            logger.warning(
                f"Filter '{filter_name}' matched message from {author_name} in #{channel_name}: "
                f"{combined_content[:100]}{'...' if len(combined_content) > 100 else ''}"
            )
            
            # Log each pattern that matched
            for match in filter_result['matches']:
                logger.warning(f"  - Matched pattern '{match['pattern']}' with text: {match['matched_text']}")
    
    # Take action if any filters matched
    if matched_filters:
        logger.info(f"Taking action on {len(matched_filters)} matched filters")
        await handle_matched_filters(message, matched_filters)
    else:
        logger.debug("No filters matched for this message")

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
    for pattern in patterns:
        try:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                matches.append({
                    'pattern': pattern,
                    'matched_text': match.group(0),
                    'start': match.start(),
                    'end': match.end()
                })
        except re.error as e:
            logger.error(f"Invalid regex pattern '{pattern}': {e}")
    
    return {
        'matches': matches,
        'description': filter_config.get('description', 'No description'),
        'action': filter_config.get('action', 'log'),
        'severity': filter_config.get('severity', 'medium')
    } if matches else None

async def handle_matched_filters(
    message: discord.Message, 
    matched_filters: List[Tuple[str, Dict]]
) -> None:
    """
    Handle matched filters by taking appropriate actions.
    
    Args:
        message: The message that matched filters
        matched_filters: List of matched filters with their results
    """
    # Determine the highest severity action
    action_priorities = {'log': 1, 'notify': 2, 'delete': 3}
    highest_action = 'log'
    highest_severity = 'low'
    
    for filter_name, filter_result in matched_filters:
        action = filter_result['action']
        severity = filter_result['severity']
        
        # Update highest action if this one has higher priority
        if action_priorities.get(action, 0) > action_priorities.get(highest_action, 0):
            highest_action = action
        
        # Update highest severity
        severity_levels = {'low': 1, 'medium': 2, 'high': 3}
        if severity_levels.get(severity, 0) > severity_levels.get(highest_severity, 0):
            highest_severity = severity
    
    # Take action based on configuration
    if highest_action == 'delete' and not config.DRY_RUN:
        try:
            await message.delete()
            logger.info(f"Deleted message from {message.author} due to filter matches: {[f[0] for f in matched_filters]}")
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
    
    # Send notification if configured
    if config.NOTIFY_FILTERED and (highest_action in ['notify', 'delete'] or config.DRY_RUN):
        await send_notification(message, matched_filters, highest_severity)

async def send_notification(
    message: discord.Message, 
    matched_filters: List[Tuple[str, Dict]],
    severity: str
) -> None:
    """
    Send notification about a filtered message.
    
    Args:
        message: The message that matched filters
        matched_filters: List of matched filters with their results
        severity: The highest severity level
    """
    if not config.NOTIFICATION_CHANNEL_ID:
        logger.warning("No notification channel configured for keyword filter")
        return
    
    # Get the notification channel
    notification_channel = message.guild.get_channel(config.NOTIFICATION_CHANNEL_ID)
    if not notification_channel:
        logger.error(f"Could not find notification channel with ID {config.NOTIFICATION_CHANNEL_ID}")
        return
    
    # Create the notification embed
    color_map = {'low': discord.Color.green(), 'medium': discord.Color.gold(), 'high': discord.Color.red()}
    embed = discord.Embed(
        title="Message Filter Alert",
        description=f"A message matched filter criteria in {message.channel.mention}"
    )
    
    # Apply styling from embed_config
    embed = embed_config.apply_default_styling(embed)
    
    # Add author information
    embed.add_field(name="Author", value=f"{message.author.mention} ({message.author})", inline=True)
    embed.add_field(name="Channel", value=message.channel.mention, inline=True)
    embed.add_field(name="Timestamp", value=f"<t:{int(message.created_at.timestamp())}:F>", inline=True)
    
    # Add matched filter information
    filter_info = []
    for filter_name, filter_result in matched_filters:
        matches = filter_result.get('matches', [])
        matched_texts = [m.get('matched_text', 'Unknown') for m in matches]
        
        filter_info.append(
            f"**{filter_name}** ({filter_result.get('severity', 'medium')}):\n"
            f"Matched: {', '.join(f'`{text}`' for text in matched_texts[:3])}"
            f"{'... and more' if len(matched_texts) > 3 else ''}"
        )
    
    embed.add_field(name="Matched Filters", value="\n".join(filter_info), inline=False)
    
    # Add message content
    content = message.content
    if len(content) > 1024:
        content = content[:1021] + "..."
    
    embed.add_field(name="Message Content", value=content or "(No text content)", inline=False)
    
    # Add action taken
    if config.DRY_RUN:
        action = "Logged only (Dry Run mode)"
    else:
        action = "Message was deleted" if any(f[1]['action'] == 'delete' for f in matched_filters) else "Message was logged"
    
    embed.add_field(name="Action Taken", value=action, inline=False)
    
    # Add message ID and link
    embed.add_field(name="Message ID", value=message.id, inline=True)
    
    try:
        # Create a link to the message if it still exists
        message_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"
        embed.add_field(name="Jump to Message", value=f"[Click here]({message_link})", inline=True)
    except:
        pass
    
    try:
        await notification_channel.send(embed=embed)
        logger.info(f"Sent notification for filtered message to channel #{notification_channel.name}")
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")

class KeywordFilter:
    def create_detection_embed(self, message, matches, rule):
        """
        Create an embed for the keyword detection notification.
        
        Args:
            message: The Discord message that triggered the detection
            matches: The matched keywords
            rule: The rule that was triggered
            
        Returns:
            discord.Embed: The detection embed
        """
        embed = discord.Embed(
            title=f"Keyword Detection: {rule.get('name', 'Unnamed Rule')}",
            description=f"Severity: **{rule.get('severity', 'Medium').capitalize()}**",
        )
        
        # Apply styling from embed_config
        embed = embed_config.apply_default_styling(embed)
        
        # Add user field
        embed.add_field(name="User:", value=f"{message.author.mention} ({message.author.name})", inline=True)
        
        # Add channel field
        embed.add_field(name="Channel:", value=f"{message.channel.mention} ({message.channel.name})", inline=True)
        
        # Timestamp based on message
        embed.timestamp = message.created_at 