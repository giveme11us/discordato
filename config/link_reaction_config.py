"""
Link Reaction Configuration

This module contains configuration settings for the link_reaction feature.
"""

import os
import json
import logging
from typing import Dict, List, Set, Any, Union
from config import mod_config
from config.settings_manager import get_manager

logger = logging.getLogger('discord_bot.config.link_reaction_config')

# Default settings
DEFAULT_CONFIG = {
    # Feature toggle
    "ENABLED": True,
    
    # Monitoring settings
    "CATEGORY_IDS": [],  # List of category IDs to monitor
    "BLACKLIST_CHANNEL_IDS": [],  # List of channel IDs to exclude from monitoring
    
    # The emoji to use for the link reaction
    "LINK_EMOJI": "🔗",  # Unicode link emoji
    
    # Store configurations
    "STORES": {
        "luisaviaroma": {
            "enabled": True,
            "name": "LUISAVIAROMA",
            "description": "Extract product IDs from LUISAVIAROMA embeds",
            "file_path": os.path.join("data", "luisaviaroma_drop_urls.txt"),
            "detection": {
                "type": "author_name",
                "value": "LUISAVIAROMA"
            },
            "extraction": {
                "primary": "url",
                "pattern": "\\/[^\\/]+\\/([^\\/]+)$",
                "fallback": "field_pid"
            }
        }
    }
}

# Initialize the settings manager with default configuration
settings_manager = get_manager("link_reaction", DEFAULT_CONFIG)

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
def LINK_EMOJI() -> str:
    return settings_manager.get("LINK_EMOJI", "🔗")

@LINK_EMOJI.setter
def LINK_EMOJI(value: str):
    settings_manager.set("LINK_EMOJI", str(value))

@property
def STORES() -> Dict[str, Dict[str, Any]]:
    return settings_manager.get("STORES", {})

@STORES.setter
def STORES(value: Dict[str, Dict[str, Any]]):
    settings_manager.set("STORES", value)

# Role whitelist from mod config
@property
def WHITELIST_ROLE_IDS() -> Set[int]:
    return mod_config.WHITELIST_ROLE_IDS

def get_store(store_id: str) -> Dict[str, Any]:
    """
    Get a specific store configuration.
    
    Args:
        store_id: Store identifier
        
    Returns:
        Store configuration dict or empty dict if not found
    """
    return STORES.get(store_id.lower(), {})

def update_store(store_id: str, config: Dict[str, Any]) -> bool:
    """
    Update a store configuration.
    
    Args:
        store_id: Store identifier
        config: New store configuration
        
    Returns:
        True if successful, False otherwise
    """
    stores = STORES.copy()
    stores[store_id.lower()] = config
    STORES = stores
    return save_config()

def delete_store(store_id: str) -> bool:
    """
    Delete a store configuration.
    
    Args:
        store_id: Store identifier
        
    Returns:
        True if successful, False otherwise
    """
    stores = STORES.copy()
    if store_id.lower() in stores:
        del stores[store_id.lower()]
        STORES = stores
        return save_config()
    return False

def save_config() -> bool:
    """
    Save the current configuration to storage.
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Saving link reaction configuration")
    return settings_manager.save_settings()

def reset_config() -> bool:
    """
    Reset configuration to defaults.
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Resetting link reaction configuration to defaults")
    return settings_manager.reset() 