"""
Configuration for the pinger module.
"""
import os
from typing import Dict, Any, List
import logging
from config.core.base_config import BaseConfig

logger = logging.getLogger(__name__)

# Default settings
DEFAULT_CONFIG = {
    "ENABLED": False,
    "MONITOR_EVERYONE": True,
    "MONITOR_HERE": True,
    "MONITOR_ROLES": True,
    "NOTIFICATION_CHANNEL_ID": None,
    "WHITELIST_ROLE_IDS": [],
    "BLACKLIST_CHANNEL_IDS": [],
    "CATEGORY_IDS": []
}

class PingerConfig(BaseConfig):
    """
    Configuration class for the pinger module.
    Handles settings for mention notifications and monitoring.
    """
    
    def __init__(self):
        """Initialize the pinger configuration."""
        config_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'data',
            'pinger_config.json'
        )
        super().__init__(config_path, DEFAULT_CONFIG, version="1.0.0")
        self._settings_manager = self  # Store the instance reference
    
    @property
    def settings_manager(self) -> 'PingerConfig':
        """Get the settings manager instance."""
        return self._settings_manager
    
    @settings_manager.setter
    def settings_manager(self, value: 'PingerConfig') -> None:
        """Set the settings manager instance."""
        self._settings_manager = value
    
    @property
    def ENABLED(self) -> bool:
        """Whether the pinger module is enabled."""
        return self.get("ENABLED", False)
    
    @ENABLED.setter
    def ENABLED(self, value: bool) -> None:
        """Set whether the pinger module is enabled."""
        self.set("ENABLED", value)
    
    @property
    def MONITOR_EVERYONE(self) -> bool:
        """Whether to monitor @everyone mentions."""
        return self.get("MONITOR_EVERYONE", True)
    
    @MONITOR_EVERYONE.setter
    def MONITOR_EVERYONE(self, value: bool) -> None:
        """Set whether to monitor @everyone mentions."""
        self.set("MONITOR_EVERYONE", value)
    
    @property
    def MONITOR_HERE(self) -> bool:
        """Whether to monitor @here mentions."""
        return self.get("MONITOR_HERE", True)
    
    @MONITOR_HERE.setter
    def MONITOR_HERE(self, value: bool) -> None:
        """Set whether to monitor @here mentions."""
        self.set("MONITOR_HERE", value)
    
    @property
    def MONITOR_ROLES(self) -> bool:
        """Whether to monitor role mentions."""
        return self.get("MONITOR_ROLES", True)
    
    @MONITOR_ROLES.setter
    def MONITOR_ROLES(self, value: bool) -> None:
        """Set whether to monitor role mentions."""
        self.set("MONITOR_ROLES", value)
    
    @property
    def NOTIFICATION_CHANNEL_ID(self) -> int:
        """The channel ID for notifications."""
        return self.get("NOTIFICATION_CHANNEL_ID")
    
    @NOTIFICATION_CHANNEL_ID.setter
    def NOTIFICATION_CHANNEL_ID(self, value: int) -> None:
        """Set the channel ID for notifications."""
        self.set("NOTIFICATION_CHANNEL_ID", value)
    
    @property
    def WHITELIST_ROLE_IDS(self) -> List[int]:
        """List of role IDs that are whitelisted from monitoring."""
        return self.get("WHITELIST_ROLE_IDS", [])
    
    @WHITELIST_ROLE_IDS.setter
    def WHITELIST_ROLE_IDS(self, value: List[int]) -> None:
        """Set the list of whitelisted role IDs."""
        self.set("WHITELIST_ROLE_IDS", value)
    
    @property
    def BLACKLIST_CHANNEL_IDS(self) -> List[int]:
        """List of channel IDs that are blacklisted from monitoring."""
        return self.get("BLACKLIST_CHANNEL_IDS", [])
    
    @BLACKLIST_CHANNEL_IDS.setter
    def BLACKLIST_CHANNEL_IDS(self, value: List[int]) -> None:
        """Set the list of blacklisted channel IDs."""
        self.set("BLACKLIST_CHANNEL_IDS", value)
    
    @property
    def CATEGORY_IDS(self) -> List[int]:
        """List of category IDs to monitor."""
        return self.get("CATEGORY_IDS", [])
    
    @CATEGORY_IDS.setter
    def CATEGORY_IDS(self, value: List[int]) -> None:
        """Set the list of category IDs to monitor."""
        self.set("CATEGORY_IDS", value)
    
    def validate_config(self) -> bool:
        """
        Validate the pinger configuration.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        if not super().validate_config():
            return False
            
        # Validate specific pinger config requirements
        try:
            # Validate channel IDs
            if self.NOTIFICATION_CHANNEL_ID is not None:
                if not isinstance(self.NOTIFICATION_CHANNEL_ID, int):
                    logger.warning("NOTIFICATION_CHANNEL_ID must be an integer")
                    return False
            
            # Validate role IDs
            for role_id in self.WHITELIST_ROLE_IDS:
                if not isinstance(role_id, int):
                    logger.warning("All WHITELIST_ROLE_IDS must be integers")
                    return False
            
            # Validate channel IDs
            for channel_id in self.BLACKLIST_CHANNEL_IDS:
                if not isinstance(channel_id, int):
                    logger.warning("All BLACKLIST_CHANNEL_IDS must be integers")
                    return False
            
            # Validate category IDs
            for category_id in self.CATEGORY_IDS:
                if not isinstance(category_id, int):
                    logger.warning("All CATEGORY_IDS must be integers")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error validating pinger config: {e}")
            return False

# Create global instance
pinger_config = PingerConfig() 