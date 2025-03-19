"""
Reaction Forward Configuration

This module contains configuration settings for the reaction_forward feature.
"""

import os
from typing import Set, List, Dict, Any, Union
import logging
from config import mod_config
from config.settings_manager import get_manager

logger = logging.getLogger('discord_bot.config.reaction_forward_config')

# Default settings
DEFAULT_CONFIG = {
    # Feature toggle
    "ENABLED": True,
    
    # Monitoring settings
    "CATEGORY_IDS": [],  # List of category IDs to monitor
    "BLACKLIST_CHANNEL_IDS": [],  # List of channel IDs to exclude from monitoring
    
    # The emoji to use for the forward reaction
    "FORWARD_EMOJI": "➡️",  # Unicode arrow_forward emoji
    
    # Whether to enable the message forwarding feature when a user reacts with the forward emoji
    "ENABLE_FORWARDING": True,
    
    # Title for forwarded message embeds
    "FORWARD_TITLE": "Forwarded Message",
    
    # Destination channel for forwarded messages (set via command)
    "DESTINATION_CHANNEL_ID": None,
    
    # Whether to include attachments when forwarding
    "FORWARD_ATTACHMENTS": True,
    
    # Whether to include embeds when forwarding
    "FORWARD_EMBEDS": True
}

# Initialize the settings manager with default configuration
settings_manager = get_manager("reaction_forward", DEFAULT_CONFIG)

# Create properties to access settings

@property
def ENABLED() -> bool:
    return settings_manager.get("ENABLED", True)

@ENABLED.setter
def ENABLED(value: bool):
    settings_manager.set("ENABLED", bool(value))

@property
def CATEGORY_IDS() -> Set[int]:
    return set(settings_manager.get("CATEGORY_IDS", []))

@CATEGORY_IDS.setter
def CATEGORY_IDS(value: Set[int]):
    settings_manager.set("CATEGORY_IDS", list(value))

@property
def BLACKLIST_CHANNEL_IDS() -> Set[int]:
    return set(settings_manager.get("BLACKLIST_CHANNEL_IDS", []))

@BLACKLIST_CHANNEL_IDS.setter
def BLACKLIST_CHANNEL_IDS(value: Set[int]):
    settings_manager.set("BLACKLIST_CHANNEL_IDS", list(value))

@property
def FORWARD_EMOJI() -> str:
    return settings_manager.get("FORWARD_EMOJI", "➡️")

@FORWARD_EMOJI.setter
def FORWARD_EMOJI(value: str):
    settings_manager.set("FORWARD_EMOJI", str(value))

@property
def ENABLE_FORWARDING() -> bool:
    return settings_manager.get("ENABLE_FORWARDING", True)

@ENABLE_FORWARDING.setter
def ENABLE_FORWARDING(value: bool):
    settings_manager.set("ENABLE_FORWARDING", bool(value))

@property
def FORWARD_TITLE() -> str:
    return settings_manager.get("FORWARD_TITLE", "Forwarded Message")

@FORWARD_TITLE.setter
def FORWARD_TITLE(value: str):
    settings_manager.set("FORWARD_TITLE", str(value))

@property
def DESTINATION_CHANNEL_ID() -> Union[int, None]:
    return settings_manager.get("DESTINATION_CHANNEL_ID")

@DESTINATION_CHANNEL_ID.setter
def DESTINATION_CHANNEL_ID(value: Union[int, None]):
    if value is not None:
        value = int(value)
    settings_manager.set("DESTINATION_CHANNEL_ID", value)

@property
def FORWARD_ATTACHMENTS() -> bool:
    return settings_manager.get("FORWARD_ATTACHMENTS", True)

@FORWARD_ATTACHMENTS.setter
def FORWARD_ATTACHMENTS(value: bool):
    settings_manager.set("FORWARD_ATTACHMENTS", bool(value))

@property
def FORWARD_EMBEDS() -> bool:
    return settings_manager.get("FORWARD_EMBEDS", True)

@FORWARD_EMBEDS.setter
def FORWARD_EMBEDS(value: bool):
    settings_manager.set("FORWARD_EMBEDS", bool(value))

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
    logger.info("Saving reaction forward configuration")
    return settings_manager.save_settings()

def reset_config() -> bool:
    """
    Reset configuration to defaults.
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Resetting reaction forward configuration to defaults")
    return settings_manager.reset() 