"""
Redeye Configuration

This module contains configuration settings for the redeye module.
"""

import os
from typing import Dict, List, Set, Union, Any
import logging
from config import mod_config
from config.settings_manager import get_manager

logger = logging.getLogger('discord_bot.config.redeye_config')

# Default settings
DEFAULT_CONFIG = {
    # Feature toggle
    "ENABLED": False,
    
    # Waitlist configurations
    "WAITLISTS": {},
    
    # Role requirements for different waitlists
    "ROLE_REQUIREMENTS": {},
    
    # Notification settings
    "NOTIFICATION_CHANNEL_ID": None,
    
    # Custom emojis for status indication
    "STATUS_EMOJIS": {
        "WAITING": "⏳",
        "APPROVED": "✅",
        "DENIED": "❌",
        "EXPIRED": "⌛"
    }
}

# Initialize the settings manager with default configuration
settings_manager = get_manager("redeye", DEFAULT_CONFIG)

# Create properties to access settings

@property
def ENABLED() -> bool:
    return settings_manager.get("ENABLED", False)

@ENABLED.setter
def ENABLED(value: bool):
    settings_manager.set("ENABLED", bool(value))

@property
def WAITLISTS() -> Dict[str, Any]:
    return settings_manager.get("WAITLISTS", {})

@WAITLISTS.setter
def WAITLISTS(value: Dict[str, Any]):
    settings_manager.set("WAITLISTS", value)

@property
def ROLE_REQUIREMENTS() -> Dict[str, List[int]]:
    return settings_manager.get("ROLE_REQUIREMENTS", {})

@ROLE_REQUIREMENTS.setter
def ROLE_REQUIREMENTS(value: Dict[str, List[int]]):
    settings_manager.set("ROLE_REQUIREMENTS", value)

@property
def NOTIFICATION_CHANNEL_ID() -> Union[int, None]:
    return settings_manager.get("NOTIFICATION_CHANNEL_ID")

@NOTIFICATION_CHANNEL_ID.setter
def NOTIFICATION_CHANNEL_ID(value: Union[int, None]):
    if value is not None:
        value = int(value)
    settings_manager.set("NOTIFICATION_CHANNEL_ID", value)

@property
def STATUS_EMOJIS() -> Dict[str, str]:
    return settings_manager.get("STATUS_EMOJIS", {})

@STATUS_EMOJIS.setter
def STATUS_EMOJIS(value: Dict[str, str]):
    settings_manager.set("STATUS_EMOJIS", value)

# Role whitelist from mod config
@property
def WHITELIST_ROLE_IDS() -> Set[int]:
    """Get whitelist roles directly from environment variable for safety"""
    import os
    
    # First, try to get direct from REDEYE_WHITELIST_ROLE_IDS env var
    whitelist_str = os.environ.get('REDEYE_WHITELIST_ROLE_IDS', '')
    whitelist_ids = set()
    
    if whitelist_str:
        try:
            # Try to parse the comma-separated list of role IDs
            whitelist_ids = {int(role_id.strip()) for role_id in whitelist_str.split(',') if role_id.strip()}
            if whitelist_ids:
                logger.debug(f"Using whitelist roles from REDEYE_WHITELIST_ROLE_IDS: {whitelist_ids}")
                return whitelist_ids
        except Exception as e:
            logger.error(f"Error parsing REDEYE_WHITELIST_ROLE_IDS from env: {e}")
    
    # Fallback to MOD_WHITELIST_ROLE_IDS env var
    whitelist_str = os.environ.get('MOD_WHITELIST_ROLE_IDS', '')
    
    if whitelist_str:
        try:
            # Try to parse the comma-separated list of role IDs
            whitelist_ids = {int(role_id.strip()) for role_id in whitelist_str.split(',') if role_id.strip()}
            if whitelist_ids:
                logger.debug(f"Using whitelist roles from MOD_WHITELIST_ROLE_IDS: {whitelist_ids}")
                return whitelist_ids
        except Exception as e:
            logger.error(f"Error parsing MOD_WHITELIST_ROLE_IDS from env: {e}")
    
    # Fallback to mod_config if direct env parsing failed
    mod_whitelist = mod_config.WHITELIST_ROLE_IDS
    logger.debug(f"Using whitelist roles from mod_config: {mod_whitelist}")
    return set(mod_whitelist)

def save_config() -> bool:
    """
    Save the current configuration to storage.
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Saving redeye configuration")
    return settings_manager.save_settings()

def reset_config() -> bool:
    """
    Reset configuration to defaults.
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Resetting redeye configuration to defaults")
    return settings_manager.reset() 