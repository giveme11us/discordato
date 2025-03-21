"""
Configuration for moderation features.
"""
import os
from typing import Dict, Any, List, Set, Optional
import logging
from config.core.base_config import BaseConfig

logger = logging.getLogger(__name__)

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

class ModConfig(BaseConfig):
    """
    Configuration class for moderator settings.
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
        """Whether moderation features are enabled."""
        return self.get("ENABLED", False)
    
    @ENABLED.setter
    def ENABLED(self, value: bool) -> None:
        """Set whether moderation features are enabled."""
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
    def LOG_CHANNEL_ID(self) -> Optional[int]:
        """The channel ID for moderation logs."""
        return self.get("LOG_CHANNEL_ID")
    
    @LOG_CHANNEL_ID.setter
    def LOG_CHANNEL_ID(self, value: Optional[int]) -> None:
        """Set the channel ID for moderation logs."""
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
            
            # Validate auto-mod settings
            if not isinstance(self.AUTO_MOD_ENABLED, bool):
                logger.warning("AUTO_MOD_ENABLED must be a boolean")
                return False
            
            if not isinstance(self.AUTO_MOD_RULES, dict):
                logger.warning("AUTO_MOD_RULES must be a dictionary")
                return False
            
            for rule, enabled in self.AUTO_MOD_RULES.items():
                if not isinstance(enabled, bool):
                    logger.warning(f"Auto-mod rule {rule} enabled status must be a boolean")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error validating config: {e}")
            return False

# Create global instances
mod = ModConfig() 