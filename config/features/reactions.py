"""
Configuration for reaction-related features.
Includes both forward and link reaction configurations.
"""
import os
from typing import Dict, Any, List, Set, Optional
import logging
from config.core.base_config import BaseConfig

logger = logging.getLogger(__name__)

# Default settings for forward reactions
FORWARD_DEFAULT_CONFIG = {
    "ENABLED": False,
    "ENABLE_FORWARDING": False,
    "CATEGORY_IDS": [],
    "MONITOR_CHANNEL_IDS": [],
    "BLACKLIST_CHANNEL_IDS": [],
    "DESTINATION_CHANNEL_ID": None,
    "FORWARD_EMOJI": "📨",
    "NOTIFICATION_CHANNEL_ID": None,
    "WHITELIST_ROLE_IDS": [],
    "INCLUDE_ATTACHMENTS": True,
    "INCLUDE_EMBEDS": True,
    "INCLUDE_STICKERS": True
}

# Default settings for link reactions
LINK_DEFAULT_CONFIG = {
    "ENABLED": False,
    "LINK_EMOJI": "🔗",
    "CATEGORY_IDS": [],
    "BLACKLIST_CHANNEL_IDS": [],
    "STORES": {
        "luisaviaroma": {
            "enabled": True,
            "emoji": "👕",
            "category_ids": [],
            "blacklist_channel_ids": []
        },
        "ssense": {
            "enabled": True,
            "emoji": "👔",
            "category_ids": [],
            "blacklist_channel_ids": []
        },
        "farfetch": {
            "enabled": True,
            "emoji": "👗",
            "category_ids": [],
            "blacklist_channel_ids": []
        }
    }
}

class ForwardConfig(BaseConfig):
    """
    Configuration class for the forward reaction feature.
    Handles settings for forwarding messages with reactions.
    """
    
    def __init__(self):
        """Initialize the forward reaction configuration."""
        config_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'data',
            'forward_reaction_config.json'
        )
        super().__init__(config_path, FORWARD_DEFAULT_CONFIG, version="1.0.0")
        self._settings_manager = self  # Store the instance reference
    
    @property
    def settings_manager(self) -> 'ForwardConfig':
        """Get the settings manager instance."""
        return self._settings_manager
    
    @settings_manager.setter
    def settings_manager(self, value: 'ForwardConfig') -> None:
        """Set the settings manager instance."""
        self._settings_manager = value
    
    @property
    def ENABLED(self) -> bool:
        """Whether the forward reaction feature is enabled."""
        return self.get("ENABLED", False)
    
    @ENABLED.setter
    def ENABLED(self, value: bool) -> None:
        """Set whether the forward reaction feature is enabled."""
        self.set("ENABLED", value)
    
    @property
    def ENABLE_FORWARDING(self) -> bool:
        """Whether message forwarding is enabled."""
        return self.get("ENABLE_FORWARDING", False)
    
    @ENABLE_FORWARDING.setter
    def ENABLE_FORWARDING(self, value: bool) -> None:
        """Set whether message forwarding is enabled."""
        self.set("ENABLE_FORWARDING", value)
    
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
    def DESTINATION_CHANNEL_ID(self) -> Optional[int]:
        """The channel ID where messages will be forwarded to."""
        return self.get("DESTINATION_CHANNEL_ID")
    
    @DESTINATION_CHANNEL_ID.setter
    def DESTINATION_CHANNEL_ID(self, value: Optional[int]) -> None:
        """Set the channel ID where messages will be forwarded to."""
        self.set("DESTINATION_CHANNEL_ID", value)
    
    @property
    def FORWARD_EMOJI(self) -> str:
        """The emoji used for forwarding messages."""
        return self.get("FORWARD_EMOJI", "📨")
    
    @FORWARD_EMOJI.setter
    def FORWARD_EMOJI(self, value: str) -> None:
        """Set the forward emoji."""
        self.set("FORWARD_EMOJI", value)
    
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
        """List of role IDs that are whitelisted."""
        return self.get("WHITELIST_ROLE_IDS", [])
    
    @WHITELIST_ROLE_IDS.setter
    def WHITELIST_ROLE_IDS(self, value: List[int]) -> None:
        """Set the list of whitelisted role IDs."""
        self.set("WHITELIST_ROLE_IDS", value)
    
    @property
    def INCLUDE_ATTACHMENTS(self) -> bool:
        """Whether to include attachments when forwarding."""
        return self.get("INCLUDE_ATTACHMENTS", True)
    
    @INCLUDE_ATTACHMENTS.setter
    def INCLUDE_ATTACHMENTS(self, value: bool) -> None:
        """Set whether to include attachments."""
        self.set("INCLUDE_ATTACHMENTS", value)
    
    @property
    def INCLUDE_EMBEDS(self) -> bool:
        """Whether to include embeds when forwarding."""
        return self.get("INCLUDE_EMBEDS", True)
    
    @INCLUDE_EMBEDS.setter
    def INCLUDE_EMBEDS(self, value: bool) -> None:
        """Set whether to include embeds."""
        self.set("INCLUDE_EMBEDS", value)
    
    @property
    def INCLUDE_STICKERS(self) -> bool:
        """Whether to include stickers when forwarding."""
        return self.get("INCLUDE_STICKERS", True)
    
    @INCLUDE_STICKERS.setter
    def INCLUDE_STICKERS(self, value: bool) -> None:
        """Set whether to include stickers."""
        self.set("INCLUDE_STICKERS", value)
    
    def validate_config(self) -> bool:
        """
        Validate the forward reaction configuration.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        if not super().validate_config():
            return False
            
        try:
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
            
            # Validate destination channel ID
            if self.DESTINATION_CHANNEL_ID is not None:
                if not isinstance(self.DESTINATION_CHANNEL_ID, int):
                    logger.warning("DESTINATION_CHANNEL_ID must be an integer")
                    return False
            
            # Validate notification channel ID
            if self.NOTIFICATION_CHANNEL_ID is not None:
                if not isinstance(self.NOTIFICATION_CHANNEL_ID, int):
                    logger.warning("NOTIFICATION_CHANNEL_ID must be an integer")
                    return False
            
            # Validate whitelist role IDs
            for role_id in self.WHITELIST_ROLE_IDS:
                if not isinstance(role_id, int):
                    logger.warning("All WHITELIST_ROLE_IDS must be integers")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error validating forward reaction config: {e}")
            return False

class LinkConfig(BaseConfig):
    """
    Configuration class for the link reaction feature.
    Handles settings for link reactions and store-specific settings.
    """
    
    def __init__(self):
        """Initialize the link reaction configuration."""
        config_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'data',
            'link_reaction_config.json'
        )
        super().__init__(config_path, LINK_DEFAULT_CONFIG, version="1.0.0")
        self._settings_manager = self  # Store the instance reference
    
    @property
    def settings_manager(self) -> 'LinkConfig':
        """Get the settings manager instance."""
        return self._settings_manager
    
    @settings_manager.setter
    def settings_manager(self, value: 'LinkConfig') -> None:
        """Set the settings manager instance."""
        self._settings_manager = value
    
    @property
    def ENABLED(self) -> bool:
        """Whether the link reaction feature is enabled."""
        return self.get("ENABLED", False)
    
    @ENABLED.setter
    def ENABLED(self, value: bool) -> None:
        """Set whether the link reaction feature is enabled."""
        self.set("ENABLED", value)
    
    @property
    def LINK_EMOJI(self) -> str:
        """The default emoji used for link reactions."""
        return self.get("LINK_EMOJI", "🔗")
    
    @LINK_EMOJI.setter
    def LINK_EMOJI(self, value: str) -> None:
        """Set the default link emoji."""
        self.set("LINK_EMOJI", value)
    
    @property
    def CATEGORY_IDS(self) -> List[int]:
        """List of category IDs to monitor."""
        return self.get("CATEGORY_IDS", [])
    
    @CATEGORY_IDS.setter
    def CATEGORY_IDS(self, value: List[int]) -> None:
        """Set the list of category IDs to monitor."""
        self.set("CATEGORY_IDS", value)
    
    @property
    def BLACKLIST_CHANNEL_IDS(self) -> List[int]:
        """List of channel IDs that are blacklisted."""
        return self.get("BLACKLIST_CHANNEL_IDS", [])
    
    @BLACKLIST_CHANNEL_IDS.setter
    def BLACKLIST_CHANNEL_IDS(self, value: List[int]) -> None:
        """Set the list of blacklisted channel IDs."""
        self.set("BLACKLIST_CHANNEL_IDS", value)
    
    @property
    def STORES(self) -> Dict[str, Dict[str, Any]]:
        """Dictionary of store-specific settings."""
        return self.get("STORES", {})
    
    @STORES.setter
    def STORES(self, value: Dict[str, Dict[str, Any]]) -> None:
        """Set the store-specific settings."""
        self.set("STORES", value)
    
    def validate_config(self) -> bool:
        """
        Validate the link reaction configuration.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        if not super().validate_config():
            return False
            
        try:
            # Validate category IDs
            for category_id in self.CATEGORY_IDS:
                if not isinstance(category_id, int):
                    logger.warning("All CATEGORY_IDS must be integers")
                    return False
            
            # Validate blacklist channel IDs
            for channel_id in self.BLACKLIST_CHANNEL_IDS:
                if not isinstance(channel_id, int):
                    logger.warning("All BLACKLIST_CHANNEL_IDS must be integers")
                    return False
            
            # Validate store configurations
            for store_name, store_config in self.STORES.items():
                # Check required fields
                required_fields = ["enabled", "emoji", "category_ids", "blacklist_channel_ids"]
                for field in required_fields:
                    if field not in store_config:
                        logger.warning(f"Store {store_name} missing required field: {field}")
                        return False
                
                # Validate types
                if not isinstance(store_config["enabled"], bool):
                    logger.warning(f"Store {store_name} enabled must be a boolean")
                    return False
                
                if not isinstance(store_config["emoji"], str):
                    logger.warning(f"Store {store_name} emoji must be a string")
                    return False
                
                if not isinstance(store_config["category_ids"], list):
                    logger.warning(f"Store {store_name} category_ids must be a list")
                    return False
                
                if not isinstance(store_config["blacklist_channel_ids"], list):
                    logger.warning(f"Store {store_name} blacklist_channel_ids must be a list")
                    return False
                
                # Validate IDs
                for category_id in store_config["category_ids"]:
                    if not isinstance(category_id, int):
                        logger.warning(f"Store {store_name} category_ids must contain integers")
                        return False
                
                for channel_id in store_config["blacklist_channel_ids"]:
                    if not isinstance(channel_id, int):
                        logger.warning(f"Store {store_name} blacklist_channel_ids must contain integers")
                        return False
            
            return True
        except Exception as e:
            logger.error(f"Error validating link reaction config: {e}")
            return False

# Create global instances
forward = ForwardConfig()
link = LinkConfig() 