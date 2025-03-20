"""
Configuration for the redeye feature.
Handles settings for profile management and task scheduling.
"""
import os
from typing import Dict, Any, List, Optional
import logging
from config.core.base_config import BaseConfig

logger = logging.getLogger(__name__)

# Default settings for redeye configuration
REDEYE_DEFAULT_CONFIG = {
    "ENABLED": False,
    "PROFILES_PATH": "data/profiles.json",
    "TASKS_PATH": "data/tasks.json",
    "NOTIFICATION_CHANNEL_ID": None,  # Added for backward compatibility
    "DEFAULT_PROFILE": {
        "name": "default",
        "description": "Default profile",
        "settings": {
            "enabled": True,
            "notify": True,
            "auto_respond": False
        }
    },
    "TASK_TYPES": {
        "check": {
            "enabled": True,
            "interval": 300,  # 5 minutes
            "timeout": 30
        },
        "update": {
            "enabled": True,
            "interval": 3600,  # 1 hour
            "timeout": 60
        }
    }
}

class RedeyeConfig(BaseConfig):
    """
    Configuration class for the redeye feature.
    Handles settings for profile management and task scheduling.
    """
    
    def __init__(self):
        """Initialize the redeye configuration."""
        config_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'data',
            'redeye_config.json'
        )
        super().__init__(config_path, REDEYE_DEFAULT_CONFIG, version="1.0.0")
    
    @property
    def ENABLED(self) -> bool:
        """Whether the redeye feature is enabled."""
        return self.get("ENABLED", False)
    
    @ENABLED.setter
    def ENABLED(self, value: bool) -> None:
        """Set whether the redeye feature is enabled."""
        self.set("ENABLED", value)
    
    @property
    def PROFILES_PATH(self) -> str:
        """Path to the profiles configuration file."""
        return self.get("PROFILES_PATH", "data/profiles.json")
    
    @PROFILES_PATH.setter
    def PROFILES_PATH(self, value: str) -> None:
        """Set the path to the profiles configuration file."""
        self.set("PROFILES_PATH", value)
    
    @property
    def TASKS_PATH(self) -> str:
        """Path to the tasks configuration file."""
        return self.get("TASKS_PATH", "data/tasks.json")
    
    @TASKS_PATH.setter
    def TASKS_PATH(self, value: str) -> None:
        """Set the path to the tasks configuration file."""
        self.set("TASKS_PATH", value)
    
    @property
    def NOTIFICATION_CHANNEL_ID(self) -> Optional[int]:
        """The channel ID for notifications."""
        return self.get("NOTIFICATION_CHANNEL_ID")
    
    @NOTIFICATION_CHANNEL_ID.setter
    def NOTIFICATION_CHANNEL_ID(self, value: Optional[int]) -> None:
        """Set the channel ID for notifications."""
        self.set("NOTIFICATION_CHANNEL_ID", value)
    
    @property
    def DEFAULT_PROFILE(self) -> Dict[str, Any]:
        """The default profile configuration."""
        return self.get("DEFAULT_PROFILE", {})
    
    @DEFAULT_PROFILE.setter
    def DEFAULT_PROFILE(self, value: Dict[str, Any]) -> None:
        """Set the default profile configuration."""
        self.set("DEFAULT_PROFILE", value)
    
    @property
    def TASK_TYPES(self) -> Dict[str, Dict[str, Any]]:
        """Dictionary of task type configurations."""
        return self.get("TASK_TYPES", {})
    
    @TASK_TYPES.setter
    def TASK_TYPES(self, value: Dict[str, Dict[str, Any]]) -> None:
        """Set the task type configurations."""
        self.set("TASK_TYPES", value)
    
    def validate_config(self) -> bool:
        """
        Validate the redeye configuration.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        if not super().validate_config():
            return False
            
        try:
            # Validate paths
            if not isinstance(self.PROFILES_PATH, str):
                logger.warning("PROFILES_PATH must be a string")
                return False
            
            if not isinstance(self.TASKS_PATH, str):
                logger.warning("TASKS_PATH must be a string")
                return False
            
            # Validate default profile
            if not isinstance(self.DEFAULT_PROFILE, dict):
                logger.warning("DEFAULT_PROFILE must be a dictionary")
                return False
            
            required_profile_fields = ["name", "description", "settings"]
            for field in required_profile_fields:
                if field not in self.DEFAULT_PROFILE:
                    logger.warning(f"DEFAULT_PROFILE missing required field: {field}")
                    return False
            
            # Validate profile settings
            settings = self.DEFAULT_PROFILE.get("settings", {})
            if not isinstance(settings, dict):
                logger.warning("Profile settings must be a dictionary")
                return False
            
            required_settings = ["enabled", "notify", "auto_respond"]
            for setting in required_settings:
                if setting not in settings:
                    logger.warning(f"Profile settings missing required field: {setting}")
                    return False
                
                if not isinstance(settings[setting], bool):
                    logger.warning(f"Profile setting {setting} must be a boolean")
                    return False
            
            # Validate task types
            if not isinstance(self.TASK_TYPES, dict):
                logger.warning("TASK_TYPES must be a dictionary")
                return False
            
            for task_type, config in self.TASK_TYPES.items():
                if not isinstance(config, dict):
                    logger.warning(f"Task type {task_type} config must be a dictionary")
                    return False
                
                required_task_fields = ["enabled", "interval", "timeout"]
                for field in required_task_fields:
                    if field not in config:
                        logger.warning(f"Task type {task_type} missing required field: {field}")
                        return False
                
                # Validate types
                if not isinstance(config["enabled"], bool):
                    logger.warning(f"Task type {task_type} enabled must be a boolean")
                    return False
                
                if not isinstance(config["interval"], (int, float)):
                    logger.warning(f"Task type {task_type} interval must be a number")
                    return False
                
                if not isinstance(config["timeout"], (int, float)):
                    logger.warning(f"Task type {task_type} timeout must be a number")
                    return False
                
                # Validate ranges
                if config["interval"] <= 0:
                    logger.warning(f"Task type {task_type} interval must be positive")
                    return False
                
                if config["timeout"] <= 0:
                    logger.warning(f"Task type {task_type} timeout must be positive")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error validating redeye config: {e}")
            return False

# Create global instance
redeye = RedeyeConfig() 