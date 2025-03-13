"""
Embed Configuration

This module contains general configuration settings for all Discord embeds used throughout the bot.
These settings are applied to all embedded notifications across all modules.
"""

import os

# Single embed color for all embeds (hex color converted to decimal for Discord)
EMBED_COLOR = int(os.getenv('EMBED_COLOR', '57fa1'), 16)

# Footer configuration
FOOTER_TEXT = os.getenv('EMBED_FOOTER_TEXT', '')
FOOTER_ICON_URL = os.getenv('EMBED_FOOTER_ICON_URL', '')

# Thumbnail configuration
THUMBNAIL_URL = os.getenv('EMBED_THUMBNAIL_URL', '')

# Author configuration (for embeds that show author information)
SHOW_AUTHOR = os.getenv('EMBED_SHOW_AUTHOR', 'False').lower() in ('true', '1', 't')
AUTHOR_NAME_OVERRIDE = os.getenv('EMBED_AUTHOR_NAME', '')  # If empty, uses the actual author name
AUTHOR_ICON_URL = os.getenv('EMBED_AUTHOR_ICON_URL', '')  # Default author icon URL

# General embed settings
DEFAULT_EMBED_TITLE = os.getenv('EMBED_DEFAULT_TITLE', 'Notification')
INCLUDE_TIMESTAMP = os.getenv('EMBED_INCLUDE_TIMESTAMP', 'True').lower() in ('true', '1', 't')

def apply_default_styling(embed, include_footer=True, include_thumbnail=True):
    """
    Apply default styling to an embed based on configuration.
    
    Args:
        embed: The Discord embed to style
        include_footer: Whether to include the footer
        include_thumbnail: Whether to include the thumbnail
        
    Returns:
        The styled embed
    """
    # Apply color
    embed.color = EMBED_COLOR
    
    # Apply timestamp if configured
    if INCLUDE_TIMESTAMP and not embed.timestamp:
        from datetime import datetime
        embed.timestamp = datetime.now()
    
    # Apply footer if configured
    if include_footer and FOOTER_TEXT:
        embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON_URL if FOOTER_ICON_URL else None)
    
    # Apply thumbnail if configured
    if include_thumbnail and THUMBNAIL_URL:
        embed.set_thumbnail(url=THUMBNAIL_URL)
    
    return embed 