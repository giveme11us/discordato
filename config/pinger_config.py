"""
Pinger Configuration

This module contains configuration settings for the pinger feature.
"""

import os
import logging
from typing import Dict, List, Set, Any, Union
from config import mod_config
from config.settings_manager import get_manager

logger = logging.getLogger('discord_bot.config.pinger_config')

# Default settings
DEFAULT_CONFIG = {
    # Feature toggle
    "ENABLED": True,
    
    # Notification settings
    "NOTIFICATION_CHANNEL_ID": None,  # Channel ID to send notifications to
    "NOTIFICATION_TITLE": "IMPORTANT PING",
    
    # Mention monitoring settings
    "MONITOR_EVERYONE": True,  # Whether to monitor @everyone pings
    "MONITOR_HERE": True,      # Whether to monitor @here pings
    "MONITOR_ROLES": False,    # Whether to monitor role pings
    
    # Embed customization
    "EMBED_COLOR": 0xFF0000,   # Red color for ping notifications
    "INCLUDE_JUMP_LINK": True  # Whether to include a jump link to the original message
}

# Initialize the settings manager with default configuration
settings_manager = get_manager("pinger", DEFAULT_CONFIG)

# Create properties to access settings

@property
def ENABLED() -> bool:
    return settings_manager.get("ENABLED", True)

@ENABLED.setter
def ENABLED(value: bool):
    settings_manager.set("ENABLED", bool(value))

@property
def NOTIFICATION_CHANNEL_ID() -> Union[int, None]:
    return settings_manager.get("NOTIFICATION_CHANNEL_ID")

@NOTIFICATION_CHANNEL_ID.setter
def NOTIFICATION_CHANNEL_ID(value: Union[int, None]):
    if value is not None:
        value = int(value)
    settings_manager.set("NOTIFICATION_CHANNEL_ID", value)

@property
def NOTIFICATION_TITLE() -> str:
    return settings_manager.get("NOTIFICATION_TITLE", "IMPORTANT PING")

@NOTIFICATION_TITLE.setter
def NOTIFICATION_TITLE(value: str):
    settings_manager.set("NOTIFICATION_TITLE", str(value))

@property
def MONITOR_EVERYONE() -> bool:
    return settings_manager.get("MONITOR_EVERYONE", True)

@MONITOR_EVERYONE.setter
def MONITOR_EVERYONE(value: bool):
    settings_manager.set("MONITOR_EVERYONE", bool(value))

@property
def MONITOR_HERE() -> bool:
    return settings_manager.get("MONITOR_HERE", True)

@MONITOR_HERE.setter
def MONITOR_HERE(value: bool):
    settings_manager.set("MONITOR_HERE", bool(value))

@property
def MONITOR_ROLES() -> bool:
    return settings_manager.get("MONITOR_ROLES", False)

@MONITOR_ROLES.setter
def MONITOR_ROLES(value: bool):
    settings_manager.set("MONITOR_ROLES", bool(value))

@property
def EMBED_COLOR() -> int:
    return settings_manager.get("EMBED_COLOR", 0xFF0000)

@EMBED_COLOR.setter
def EMBED_COLOR(value: int):
    settings_manager.set("EMBED_COLOR", int(value))

@property
def INCLUDE_JUMP_LINK() -> bool:
    return settings_manager.get("INCLUDE_JUMP_LINK", True)

@INCLUDE_JUMP_LINK.setter
def INCLUDE_JUMP_LINK(value: bool):
    settings_manager.set("INCLUDE_JUMP_LINK", bool(value))

# Role whitelist from mod config
@property
def WHITELIST_ROLE_IDS() -> Set[int]:
    return mod_config.WHITELIST_ROLE_IDS

def save_config() -> bool:
    """
    Save the current configuration to storage.
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Saving pinger configuration")
    return settings_manager.save_settings()

def reset_config() -> bool:
    """
    Reset configuration to defaults.
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Resetting pinger configuration to defaults")
    return settings_manager.reset() 