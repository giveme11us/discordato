"""
Embed Configuration

This module contains general configuration settings for all Discord embeds used throughout the bot.
These settings are applied to all embedded notifications across all modules.
"""

import os
from typing import Optional
from discord import Embed
from datetime import datetime

class EmbedConfig:
    """Configuration class for Discord embed styling."""
    
    def __init__(self):
        # Single embed color for all embeds (hex color converted to decimal for Discord)
        self.EMBED_COLOR = int(os.getenv('EMBED_COLOR', '57fa1'), 16)

        # Footer configuration
        self.FOOTER_TEXT = os.getenv('EMBED_FOOTER_TEXT', '')
        self.FOOTER_ICON_URL = os.getenv('EMBED_FOOTER_ICON_URL', '')

        # Thumbnail configuration
        self.THUMBNAIL_URL = os.getenv('EMBED_THUMBNAIL_URL', '')

        # Author configuration (for embeds that show author information)
        self.SHOW_AUTHOR = os.getenv('EMBED_SHOW_AUTHOR', 'False').lower() in ('true', '1', 't')
        self.AUTHOR_NAME_OVERRIDE = os.getenv('EMBED_AUTHOR_NAME', '')  # If empty, uses the actual author name
        self.AUTHOR_ICON_URL = os.getenv('EMBED_AUTHOR_ICON_URL', '')  # Default author icon URL

        # General embed settings
        self.DEFAULT_EMBED_TITLE = os.getenv('EMBED_DEFAULT_TITLE', 'Notification')
        self.INCLUDE_TIMESTAMP = os.getenv('EMBED_INCLUDE_TIMESTAMP', 'True').lower() in ('true', '1', 't')

    def apply_default_styling(self, embed: Embed, include_footer: bool = True, include_thumbnail: bool = True) -> Embed:
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
        embed.color = self.EMBED_COLOR
        
        # Apply timestamp if configured
        if self.INCLUDE_TIMESTAMP and not embed.timestamp:
            embed.timestamp = datetime.now()
        
        # Apply footer if configured
        if include_footer and self.FOOTER_TEXT:
            embed.set_footer(text=self.FOOTER_TEXT, icon_url=self.FOOTER_ICON_URL if self.FOOTER_ICON_URL else None)
        
        # Apply thumbnail if configured
        if include_thumbnail and self.THUMBNAIL_URL:
            embed.set_thumbnail(url=self.THUMBNAIL_URL)
        
        return embed

# Create and export the config instance
embed = EmbedConfig() 