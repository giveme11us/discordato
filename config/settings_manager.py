"""
Settings Manager

This module provides a centralized way to manage persistent settings for all bot modules.
It handles loading, saving, and validating configuration.
"""

import os
import json
import logging
import threading
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger('discord_bot.config.settings_manager')

# Directory where all settings files are stored
SETTINGS_DIR = os.path.join('data', 'settings')

# Make sure directory exists
try:
    os.makedirs(SETTINGS_DIR, exist_ok=True)
    logger.info(f"Settings directory ready: {SETTINGS_DIR}")
except Exception as e:
    logger.error(f"Error creating settings directory: {e}")

# Lock for thread-safe file operations
file_lock = threading.Lock()

class SettingsManager:
    """Manager for module settings that handles persistence and validation."""
    
    def __init__(self, module_name: str, default_settings: Dict[str, Any]):
        """
        Initialize the settings manager for a module.
        
        Args:
            module_name: The name of the module (used for the filename)
            default_settings: Default settings to use if no file exists
        """
        self.module_name = module_name
        self.default_settings = default_settings
        self.settings = {}
        self.settings_file = os.path.join(SETTINGS_DIR, f"{module_name.lower()}.json")
        self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """
        Load settings from the JSON file.
        
        Returns:
            The loaded settings
        """
        with file_lock:
            try:
                if os.path.exists(self.settings_file):
                    logger.info(f"Loading settings from {self.settings_file}")
                    with open(self.settings_file, 'r', encoding='utf-8') as f:
                        loaded_settings = json.load(f)
                        
                    # Deep merge with defaults to ensure all required keys exist
                    self.settings = self._deep_merge(self.default_settings, loaded_settings)
                    logger.info(f"Loaded settings for module {self.module_name}")
                else:
                    # Use defaults if no file exists
                    self.settings = self.default_settings.copy()
                    logger.info(f"No settings file found for {self.module_name}, using defaults")
                    
                    # Save defaults to create the file
                    self.save_settings()
            except Exception as e:
                logger.error(f"Error loading settings for {self.module_name}: {str(e)}")
                self.settings = self.default_settings.copy()
                
        return self.settings
    
    def save_settings(self) -> bool:
        """
        Save current settings to the JSON file.
        
        Returns:
            True if successful, False otherwise
        """
        with file_lock:
            try:
                # Double-check directory exists
                os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
                
                logger.info(f"Saving settings to {self.settings_file}")
                
                # Write to a temporary file first
                temp_file = f"{self.settings_file}.tmp"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(self.settings, f, indent=2)
                
                # Then rename it to the actual file name
                if os.path.exists(self.settings_file):
                    os.replace(temp_file, self.settings_file)
                else:
                    os.rename(temp_file, self.settings_file)
                    
                logger.info(f"Saved settings for module {self.module_name}")
                return True
            except Exception as e:
                logger.error(f"Error saving settings for {self.module_name}: {str(e)}")
                return False
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Get a setting value.
        
        Args:
            key: The setting key
            default: Default value if key doesn't exist
            
        Returns:
            The setting value or default
        """
        # Support nested keys with dot notation (e.g., "filters.scam_links.enabled")
        if "." in key:
            parts = key.split(".")
            value = self.settings
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return default
            return value
        
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any, save: bool = True) -> bool:
        """
        Set a setting value.
        
        Args:
            key: The setting key
            value: The value to set
            save: Whether to save to disk immediately
            
        Returns:
            True if successful, False otherwise
        """
        # Support nested keys with dot notation
        if "." in key:
            parts = key.split(".")
            target = self.settings
            for part in parts[:-1]:
                if part not in target:
                    target[part] = {}
                target = target[part]
            target[parts[-1]] = value
        else:
            self.settings[key] = value
        
        if save:
            return self.save_settings()
        return True
    
    def update(self, settings_dict: Dict[str, Any], save: bool = True) -> bool:
        """
        Update multiple settings at once.
        
        Args:
            settings_dict: Dictionary of settings to update
            save: Whether to save to disk immediately
            
        Returns:
            True if successful, False otherwise
        """
        self.settings.update(settings_dict)
        if save:
            return self.save_settings()
        return True
    
    def reset(self, save: bool = True) -> bool:
        """
        Reset settings to defaults.
        
        Args:
            save: Whether to save to disk immediately
            
        Returns:
            True if successful, False otherwise
        """
        self.settings = self.default_settings.copy()
        if save:
            return self.save_settings()
        return True
    
    def reset_key(self, key: str, save: bool = True) -> bool:
        """
        Reset a specific setting to its default value.
        
        Args:
            key: The setting key
            save: Whether to save to disk immediately
            
        Returns:
            True if successful, False otherwise
        """
        # Support nested keys with dot notation
        if "." in key:
            parts = key.split(".")
            default_value = self.default_settings
            for part in parts:
                if isinstance(default_value, dict) and part in default_value:
                    default_value = default_value[part]
                else:
                    return False
                    
            current = self.settings
            for part in parts[:-1]:
                if part not in current:
                    return False
                current = current[part]
            
            current[parts[-1]] = default_value
        else:
            if key in self.default_settings:
                self.settings[key] = self.default_settings[key]
            else:
                return False
        
        if save:
            return self.save_settings()
        return True
    
    def _deep_merge(self, default: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries, with override values taking precedence.
        Ensures all keys from default exist in the result.
        
        Args:
            default: The default dictionary
            override: The override dictionary
            
        Returns:
            Merged dictionary
        """
        result = default.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result

# Global registry of setting managers
_managers: Dict[str, SettingsManager] = {}

def get_manager(module_name: str, default_settings: Optional[Dict[str, Any]] = None) -> SettingsManager:
    """
    Get or create a settings manager for a module.
    
    Args:
        module_name: The name of the module
        default_settings: Default settings to use if creating a new manager
        
    Returns:
        A settings manager instance
    """
    if module_name in _managers:
        return _managers[module_name]
    
    if default_settings is None:
        default_settings = {}
        
    manager = SettingsManager(module_name, default_settings)
    _managers[module_name] = manager
    
    return manager 