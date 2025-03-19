"""
Keyword Filter Configuration

This module defines the configuration settings for the keyword filter feature.
"""

from typing import Dict, List, Set, Union, Any
import logging
import os
from config.settings_manager import get_manager

logger = logging.getLogger('discord_bot.config.keyword_filter_config')

# Default filter configuration
DEFAULT_CONFIG = {
    # Feature toggle
    "ENABLED": False,  # Set to True to enable keyword filtering
    
    # Dry run mode (log only, no actions taken)
    "DRY_RUN": True,  # Set to False to enable real actions (message deletion)
    
    # Notification settings
    "NOTIFICATION_CHANNEL_ID": None,  # Default channel ID to send notifications to (fallback)
    "NOTIFY_FILTERED": True,  # Whether to send notifications for filtered messages
    
    # Legacy monitoring settings (used as fallback)
    "CATEGORY_IDS": [],  # List of category IDs to monitor
    "MONITOR_CHANNEL_IDS": [],  # List of specific channel IDs to monitor
    "BLACKLIST_CHANNEL_IDS": [],  # List of channel IDs to exclude from monitoring
    
    # Named rules - each rule has its own monitors, alerts, and keywords
    "RULES": {
        # Example rule (not active by default)
        "example_rule": {
            "enabled": False,
            "name": "Example Rule",
            "description": "An example rule that monitors for specific keywords",
            "category_ids": [],  # Categories to monitor
            "channel_ids": [],   # Specific channels to monitor
            "blacklist_ids": [], # Channels to exclude from monitoring
            "alert_channel_id": None,  # Where to send alerts for this rule
            "severity": "medium",      # low, medium, high
            "action": "notify",        # log, notify, delete
            "keywords": []             # List of keywords/patterns to match
        }
    },
    
    # Legacy Filter definitions (maintained for backward compatibility)
    "FILTERS": {
        "scam_links": {
            "enabled": True,
            "patterns": [
                r"discord\.gift\/[a-zA-Z0-9]+",
                r"nitro\s+for\s+free",
                r"free\s+nitro\s+generator",
                r"steam\s+community\.com\/tradeoffer"
            ],
            "description": "Filters common Discord nitro scam patterns",
            "action": "notify",
            "severity": "high"
        },
        "invite_links": {
            "enabled": True,
            "patterns": [
                r"discord\.gg\/[a-zA-Z0-9]+",
                r"discordapp\.com\/invite\/[a-zA-Z0-9]+"
            ],
            "description": "Filters Discord server invite links",
            "action": "notify",
            "severity": "medium"
        },
        "inappropriate_content": {
            "enabled": True,
            "patterns": [
                r"(^|\s)nsfw(\s|$)",
                r"(^|\s)18\+(\s|$)"
            ],
            "description": "Filters inappropriate content references",
            "action": "log",
            "severity": "medium"
        }
    }
}

# Initialize the settings manager with default configuration
settings_manager = get_manager("keyword_filter", DEFAULT_CONFIG)

# Create properties to access settings

@property
def ENABLED() -> bool:
    return settings_manager.get("ENABLED", False)

@ENABLED.setter
def ENABLED(value: bool):
    settings_manager.set("ENABLED", bool(value))

@property
def DRY_RUN() -> bool:
    return settings_manager.get("DRY_RUN", True)

@DRY_RUN.setter
def DRY_RUN(value: bool):
    settings_manager.set("DRY_RUN", bool(value))

@property
def NOTIFICATION_CHANNEL_ID() -> Union[int, None]:
    return settings_manager.get("NOTIFICATION_CHANNEL_ID")

@NOTIFICATION_CHANNEL_ID.setter
def NOTIFICATION_CHANNEL_ID(value: Union[int, None]):
    if value is not None:
        value = int(value)
    settings_manager.set("NOTIFICATION_CHANNEL_ID", value)

@property
def NOTIFY_FILTERED() -> bool:
    return settings_manager.get("NOTIFY_FILTERED", True)

@NOTIFY_FILTERED.setter
def NOTIFY_FILTERED(value: bool):
    settings_manager.set("NOTIFY_FILTERED", bool(value))

@property
def CATEGORY_IDS() -> Set[int]:
    return set(settings_manager.get("CATEGORY_IDS", []))

@CATEGORY_IDS.setter
def CATEGORY_IDS(value: Set[int]):
    settings_manager.set("CATEGORY_IDS", list(value))

@property
def MONITOR_CHANNEL_IDS() -> Set[int]:
    return set(settings_manager.get("MONITOR_CHANNEL_IDS", []))

@MONITOR_CHANNEL_IDS.setter
def MONITOR_CHANNEL_IDS(value: Set[int]):
    settings_manager.set("MONITOR_CHANNEL_IDS", list(value))

@property
def BLACKLIST_CHANNEL_IDS() -> Set[int]:
    return set(settings_manager.get("BLACKLIST_CHANNEL_IDS", []))

@BLACKLIST_CHANNEL_IDS.setter
def BLACKLIST_CHANNEL_IDS(value: Set[int]):
    settings_manager.set("BLACKLIST_CHANNEL_IDS", list(value))

@property
def RULES() -> Dict[str, Dict[str, Any]]:
    return settings_manager.get("RULES", {})

@RULES.setter
def RULES(value: Dict[str, Dict[str, Any]]):
    settings_manager.set("RULES", value)

@property
def FILTERS() -> Dict[str, Dict[str, Any]]:
    return settings_manager.get("FILTERS", {})

@FILTERS.setter
def FILTERS(value: Dict[str, Dict[str, Any]]):
    settings_manager.set("FILTERS", value)

def save_config() -> bool:
    """
    Save the current configuration to storage.
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Saving keyword filter configuration")
    return settings_manager.save_settings()

def reset_config() -> bool:
    """
    Reset configuration to defaults.
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Resetting keyword filter configuration to defaults")
    return settings_manager.reset()

# Legacy compatibility for direct attribute access (will be deprecated in future)
# This allows old code to still work while we transition to the new system
_CURRENT_CONFIG = None

def _get_current_config():
    global _CURRENT_CONFIG
    if _CURRENT_CONFIG is None:
        _CURRENT_CONFIG = CurrentConfig()
    return _CURRENT_CONFIG

class CurrentConfig:
    def __getattr__(self, name):
        # Forward attribute access to module properties
        try:
            return globals()[name]
        except KeyError:
            raise AttributeError(f"'CurrentConfig' has no attribute '{name}'")
    
    def __setattr__(self, name, value):
        # Forward attribute assignment to module properties
        try:
            setter = globals()[name].fset
            setter(value)
        except (KeyError, AttributeError):
            # If not a property, set directly on instance
            object.__setattr__(self, name, value)

# Initialize current config for backward compatibility
_current_config = _get_current_config()

def get_active_filters() -> Dict[str, Dict[str, Union[bool, List[str], str]]]:
    """
    Returns a dictionary of active filters.
    
    Returns:
        Dict of active filters
    """
    return {name: settings for name, settings in FILTERS.items() if settings.get('enabled', False)}

def is_monitoring_channel(channel_id: int, category_id: int = None) -> bool:
    """
    Check if a channel is being monitored.
    
    Args:
        channel_id: The channel ID to check
        category_id: The category ID the channel belongs to (optional)
        
    Returns:
        Bool indicating if the channel should be monitored
    """
    # Skip blacklisted channels
    if channel_id in BLACKLIST_CHANNEL_IDS:
        return False
        
    # Check if channel's category is monitored
    if category_id and category_id in CATEGORY_IDS:
        return True
        
    return False

# Note: Configuration is loaded automatically by the settings_manager 