"""
Configuration for moderation features.
Includes both keyword filtering and moderator settings.
"""
import os
from typing import Dict, Any, List, Set, Optional
import logging
from config.core.base_config import BaseConfig

logger = logging.getLogger(__name__)

# Default settings for keyword filtering
FILTER_DEFAULT_CONFIG = {
    "ENABLED": False,
    "DRY_RUN": True,  # Set to True by default for safety
    "CATEGORY_IDS": [],
    "MONITOR_CHANNEL_IDS": [],  # Added for backward compatibility
    "BLACKLIST_CHANNEL_IDS": [],
    "NOTIFICATION_CHANNEL_ID": None,  # Channel for filter notifications
    "RULES": {},  # Dictionary of filter rules
    "FILTERS": {
        "spam": {
            "enabled": True,
            "patterns": [],
            "action": "delete",
            "notify": True
        },
        "links": {
            "enabled": True,
            "patterns": [],
            "action": "delete",
            "notify": True
        },
        "caps": {
            "enabled": True,
            "threshold": 0.7,
            "action": "warn",
            "notify": True
        }
    }
}

# Default settings for moderator configuration
MOD_DEFAULT_CONFIG = {
    "ENABLED": False,
    "WHITELIST_ROLE_IDS": [],
    "BLACKLIST_ROLE_IDS": [],
    "MOD_CHANNEL_IDS": [],
    "LOG_CHANNEL_ID": None,
    "AUTO_MOD_ENABLED": False,
    "AUTO_MOD_RULES": {
        "spam": True,
        "links": True,
        "caps": True,
        "mentions": True
    }
}

class FilterConfig(BaseConfig):
    """
    Configuration class for the keyword filter feature.
    Handles settings for filtering messages based on keywords and patterns.
    """
    
    def __init__(self):
        """Initialize the filter configuration."""
        config_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'data',
            'filter_config.json'
        )
        super().__init__(config_path, FILTER_DEFAULT_CONFIG, version="1.0.0")
    
    @property
    def ENABLED(self) -> bool:
        """Whether the filter feature is enabled."""
        return self.get("ENABLED", False)
    
    @ENABLED.setter
    def ENABLED(self, value: bool) -> None:
        """Set whether the filter feature is enabled."""
        self.set("ENABLED", value)
    
    @property
    def DRY_RUN(self) -> bool:
        """Whether to run in dry run mode (no actions taken)."""
        return self.get("DRY_RUN", True)
    
    @DRY_RUN.setter
    def DRY_RUN(self, value: bool) -> None:
        """Set whether to run in dry run mode."""
        self.set("DRY_RUN", value)
    
    @property
    def CATEGORY_IDS(self) -> List[int]:
        """List of category IDs to monitor."""
        return self.get("CATEGORY_IDS", [])
    
    @CATEGORY_IDS.setter
    def CATEGORY_IDS(self, value: List[int]) -> None:
        """Set the list of category IDs to monitor."""
        self.set("CATEGORY_IDS", value)
    
    @property
    def MONITOR_CHANNEL_IDS(self) -> List[int]:
        """List of channel IDs to monitor."""
        return self.get("MONITOR_CHANNEL_IDS", [])
    
    @MONITOR_CHANNEL_IDS.setter
    def MONITOR_CHANNEL_IDS(self, value: List[int]) -> None:
        """Set the list of channel IDs to monitor."""
        self.set("MONITOR_CHANNEL_IDS", value)
    
    @property
    def BLACKLIST_CHANNEL_IDS(self) -> List[int]:
        """List of channel IDs that are blacklisted."""
        return self.get("BLACKLIST_CHANNEL_IDS", [])
    
    @BLACKLIST_CHANNEL_IDS.setter
    def BLACKLIST_CHANNEL_IDS(self, value: List[int]) -> None:
        """Set the list of blacklisted channel IDs."""
        self.set("BLACKLIST_CHANNEL_IDS", value)
    
    @property
    def NOTIFICATION_CHANNEL_ID(self) -> Optional[int]:
        """The channel ID for filter notifications."""
        return self.get("NOTIFICATION_CHANNEL_ID")
    
    @NOTIFICATION_CHANNEL_ID.setter
    def NOTIFICATION_CHANNEL_ID(self, value: Optional[int]) -> None:
        """Set the channel ID for filter notifications."""
        self.set("NOTIFICATION_CHANNEL_ID", value)
    
    @property
    def RULES(self) -> Dict[str, Dict[str, Any]]:
        """Dictionary of filter rules."""
        return self.get("RULES", {})
    
    @RULES.setter
    def RULES(self, value: Dict[str, Dict[str, Any]]) -> None:
        """Set the filter rules."""
        self.set("RULES", value)
    
    @property
    def FILTERS(self) -> Dict[str, Dict[str, Any]]:
        """Dictionary of filter configurations."""
        return self.get("FILTERS", {})
    
    @FILTERS.setter
    def FILTERS(self, value: Dict[str, Dict[str, Any]]) -> None:
        """Set the filter configurations."""
        self.set("FILTERS", value)
    
    def validate_config(self) -> bool:
        """
        Validate the filter configuration.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        if not super().validate_config():
            return False
            
        try:
            # Validate DRY_RUN
            if not isinstance(self.DRY_RUN, bool):
                logger.warning("DRY_RUN must be a boolean")
                return False
            
            # Validate category IDs
            for category_id in self.CATEGORY_IDS:
                if not isinstance(category_id, int):
                    logger.warning("All CATEGORY_IDS must be integers")
                    return False
            
            # Validate monitor channel IDs
            for channel_id in self.MONITOR_CHANNEL_IDS:
                if not isinstance(channel_id, int):
                    logger.warning("All MONITOR_CHANNEL_IDS must be integers")
                    return False
            
            # Validate blacklist channel IDs
            for channel_id in self.BLACKLIST_CHANNEL_IDS:
                if not isinstance(channel_id, int):
                    logger.warning("All BLACKLIST_CHANNEL_IDS must be integers")
                    return False
            
            # Validate notification channel ID
            if self.NOTIFICATION_CHANNEL_ID is not None:
                if not isinstance(self.NOTIFICATION_CHANNEL_ID, int):
                    logger.warning("NOTIFICATION_CHANNEL_ID must be an integer")
                    return False
            
            # Validate rules
            for rule_id, rule in self.RULES.items():
                if not isinstance(rule, dict):
                    logger.warning(f"Rule {rule_id} must be a dictionary")
                    return False
                
                # Check required fields
                required_fields = ["enabled", "keywords", "action"]
                for field in required_fields:
                    if field not in rule:
                        logger.warning(f"Rule {rule_id} missing required field: {field}")
                        return False
                
                # Validate types
                if not isinstance(rule["enabled"], bool):
                    logger.warning(f"Rule {rule_id} enabled must be a boolean")
                    return False
                
                if not isinstance(rule["keywords"], list):
                    logger.warning(f"Rule {rule_id} keywords must be a list")
                    return False
                
                if not isinstance(rule["action"], str):
                    logger.warning(f"Rule {rule_id} action must be a string")
                    return False
                
                # Validate action
                if rule["action"] not in ["delete", "warn", "mute", "kick", "ban"]:
                    logger.warning(f"Rule {rule_id} has invalid action: {rule['action']}")
                    return False
                
                # Validate optional fields
                if "category_ids" in rule:
                    if not isinstance(rule["category_ids"], list):
                        logger.warning(f"Rule {rule_id} category_ids must be a list")
                        return False
                    for category_id in rule["category_ids"]:
                        if not isinstance(category_id, int):
                            logger.warning(f"Rule {rule_id} category_ids must contain integers")
                            return False
                
                if "channel_ids" in rule:
                    if not isinstance(rule["channel_ids"], list):
                        logger.warning(f"Rule {rule_id} channel_ids must be a list")
                        return False
                    for channel_id in rule["channel_ids"]:
                        if not isinstance(channel_id, int):
                            logger.warning(f"Rule {rule_id} channel_ids must contain integers")
                            return False
                
                if "blacklist_ids" in rule:
                    if not isinstance(rule["blacklist_ids"], list):
                        logger.warning(f"Rule {rule_id} blacklist_ids must be a list")
                        return False
                    for channel_id in rule["blacklist_ids"]:
                        if not isinstance(channel_id, int):
                            logger.warning(f"Rule {rule_id} blacklist_ids must contain integers")
                            return False
                
                if "alert_channel_id" in rule:
                    if not isinstance(rule["alert_channel_id"], int):
                        logger.warning(f"Rule {rule_id} alert_channel_id must be an integer")
                        return False
            
            return True
        except Exception as e:
            logger.error(f"Error validating filter config: {e}")
            return False

class ModConfig(BaseConfig):
    """
    Configuration class for moderator settings.
    Handles settings for moderator roles, channels, and auto-moderation.
    """
    
    def __init__(self):
        """Initialize the moderator configuration."""
        config_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'data',
            'mod_config.json'
        )
        super().__init__(config_path, MOD_DEFAULT_CONFIG, version="1.0.0")
    
    @property
    def ENABLED(self) -> bool:
        """Whether the moderator feature is enabled."""
        return self.get("ENABLED", False)
    
    @ENABLED.setter
    def ENABLED(self, value: bool) -> None:
        """Set whether the moderator feature is enabled."""
        self.set("ENABLED", value)
    
    @property
    def WHITELIST_ROLE_IDS(self) -> List[int]:
        """List of whitelisted role IDs."""
        return self.get("WHITELIST_ROLE_IDS", [])
    
    @WHITELIST_ROLE_IDS.setter
    def WHITELIST_ROLE_IDS(self, value: List[int]) -> None:
        """Set the list of whitelisted role IDs."""
        self.set("WHITELIST_ROLE_IDS", value)
    
    @property
    def BLACKLIST_ROLE_IDS(self) -> List[int]:
        """List of blacklisted role IDs."""
        return self.get("BLACKLIST_ROLE_IDS", [])
    
    @BLACKLIST_ROLE_IDS.setter
    def BLACKLIST_ROLE_IDS(self, value: List[int]) -> None:
        """Set the list of blacklisted role IDs."""
        self.set("BLACKLIST_ROLE_IDS", value)
    
    @property
    def MOD_CHANNEL_IDS(self) -> List[int]:
        """List of moderator channel IDs."""
        return self.get("MOD_CHANNEL_IDS", [])
    
    @MOD_CHANNEL_IDS.setter
    def MOD_CHANNEL_IDS(self, value: List[int]) -> None:
        """Set the list of moderator channel IDs."""
        self.set("MOD_CHANNEL_IDS", value)
    
    @property
    def LOG_CHANNEL_ID(self) -> int:
        """The channel ID for logging."""
        return self.get("LOG_CHANNEL_ID")
    
    @LOG_CHANNEL_ID.setter
    def LOG_CHANNEL_ID(self, value: int) -> None:
        """Set the channel ID for logging."""
        self.set("LOG_CHANNEL_ID", value)
    
    @property
    def AUTO_MOD_ENABLED(self) -> bool:
        """Whether auto-moderation is enabled."""
        return self.get("AUTO_MOD_ENABLED", False)
    
    @AUTO_MOD_ENABLED.setter
    def AUTO_MOD_ENABLED(self, value: bool) -> None:
        """Set whether auto-moderation is enabled."""
        self.set("AUTO_MOD_ENABLED", value)
    
    @property
    def AUTO_MOD_RULES(self) -> Dict[str, bool]:
        """Dictionary of auto-moderation rules."""
        return self.get("AUTO_MOD_RULES", {})
    
    @AUTO_MOD_RULES.setter
    def AUTO_MOD_RULES(self, value: Dict[str, bool]) -> None:
        """Set the auto-moderation rules."""
        self.set("AUTO_MOD_RULES", value)
    
    def validate_config(self) -> bool:
        """
        Validate the moderator configuration.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        if not super().validate_config():
            return False
            
        try:
            # Validate role IDs
            for role_id in self.WHITELIST_ROLE_IDS:
                if not isinstance(role_id, int):
                    logger.warning("All WHITELIST_ROLE_IDS must be integers")
                    return False
            
            for role_id in self.BLACKLIST_ROLE_IDS:
                if not isinstance(role_id, int):
                    logger.warning("All BLACKLIST_ROLE_IDS must be integers")
                    return False
            
            # Validate channel IDs
            for channel_id in self.MOD_CHANNEL_IDS:
                if not isinstance(channel_id, int):
                    logger.warning("All MOD_CHANNEL_IDS must be integers")
                    return False
            
            if self.LOG_CHANNEL_ID is not None:
                if not isinstance(self.LOG_CHANNEL_ID, int):
                    logger.warning("LOG_CHANNEL_ID must be an integer")
                    return False
            
            # Validate auto-mod rules
            for rule_name, enabled in self.AUTO_MOD_RULES.items():
                if not isinstance(enabled, bool):
                    logger.warning(f"Auto-mod rule {rule_name} must be a boolean")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error validating mod config: {e}")
            return False

# Create global instances
filter = FilterConfig()
mod = ModConfig() 