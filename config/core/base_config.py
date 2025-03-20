"""
Base configuration class providing common functionality for all config objects.
"""
import json
import os
import shutil
from datetime import datetime
from typing import Any, Dict, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class BaseConfig:
    """
    Base configuration class that provides common functionality for all config objects.
    Includes validation, migration, and backup capabilities.
    """
    
    def __init__(self, config_path: str, default_config: Dict[str, Any], version: str = "1.0.0"):
        """
        Initialize the configuration.
        
        Args:
            config_path: Path to the configuration file
            default_config: Default configuration values
            version: Current version of the configuration schema
        """
        self.config_path = config_path
        self.default_config = default_config
        self.version = version
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file or create with defaults."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self._config = json.load(f)
                    # Check if migration is needed
                    if self._config.get('version') != self.version:
                        self.migrate_config(self._config.get('version', '0.0.0'), self.version)
            else:
                self._config = self.default_config.copy()
                self._config['version'] = self.version
                self.save_config()
        except Exception as e:
            logger.error(f"Error loading config from {self.config_path}: {e}")
            self._config = self.default_config.copy()
            self._config['version'] = self.version
            self.save_config()
    
    def save_config(self) -> bool:
        """
        Save the current configuration to file.
        
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            # Create backup before saving
            self.backup_config()
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Save new config
            with open(self.config_path, 'w') as f:
                json.dump(self._config, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Error saving config to {self.config_path}: {e}")
            return False
    
    def backup_config(self) -> None:
        """Create a backup of the current configuration."""
        if not os.path.exists(self.config_path):
            return
            
        try:
            # Create backups directory if it doesn't exist
            backup_dir = os.path.join(os.path.dirname(self.config_path), 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(
                backup_dir,
                f"{os.path.basename(self.config_path)}.{timestamp}.bak"
            )
            
            # Copy current config to backup
            shutil.copy2(self.config_path, backup_path)
            
            # Clean up old backups (keep last 5)
            self._cleanup_old_backups(backup_dir)
            
            logger.info(f"Created backup at {backup_path}")
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
    
    def _cleanup_old_backups(self, backup_dir: str, max_backups: int = 5) -> None:
        """
        Clean up old backup files, keeping only the most recent ones.
        
        Args:
            backup_dir: Directory containing backup files
            max_backups: Maximum number of backup files to keep
        """
        try:
            # Get all backup files
            backup_files = [
                f for f in os.listdir(backup_dir)
                if f.endswith('.bak')
            ]
            
            # Sort by modification time (newest first)
            backup_files.sort(
                key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)),
                reverse=True
            )
            
            # Remove old backups
            for old_backup in backup_files[max_backups:]:
                os.remove(os.path.join(backup_dir, old_backup))
                logger.info(f"Removed old backup: {old_backup}")
        except Exception as e:
            logger.error(f"Error cleaning up old backups: {e}")
    
    def restore_backup(self, backup_path: str) -> bool:
        """
        Restore configuration from a backup file.
        
        Args:
            backup_path: Path to the backup file to restore from
            
        Returns:
            bool: True if restore was successful, False otherwise
        """
        try:
            if not os.path.exists(backup_path):
                logger.error(f"Backup file not found: {backup_path}")
                return False
                
            # Create backup of current config before restoring
            self.backup_config()
            
            # Restore from backup
            shutil.copy2(backup_path, self.config_path)
            
            # Reload config
            self._load_config()
            
            logger.info(f"Successfully restored from backup: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error restoring from backup: {e}")
            return False
    
    def validate_config(self) -> bool:
        """
        Validate the current configuration.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        try:
            # Check required fields
            for key, value in self.default_config.items():
                if key not in self._config:
                    logger.warning(f"Missing required config field: {key}")
                    return False
                    
                # Validate type
                if not isinstance(self._config[key], type(value)):
                    logger.warning(
                        f"Invalid type for {key}: expected {type(value)}, "
                        f"got {type(self._config[key])}"
                    )
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error validating config: {e}")
            return False
    
    def migrate_config(self, old_version: str, new_version: str) -> None:
        """
        Migrate configuration from old version to new version.
        
        Args:
            old_version: Current version of the configuration
            new_version: Target version to migrate to
        """
        try:
            # Add migration logic here based on version changes
            # Example:
            # if old_version == "1.0.0" and new_version == "1.1.0":
            #     self._migrate_1_0_0_to_1_1_0()
            
            # Update version
            self._config['version'] = new_version
            self.save_config()
            
            logger.info(f"Migrated config from {old_version} to {new_version}")
        except Exception as e:
            logger.error(f"Error migrating config: {e}")
            # Restore from backup if migration fails
            self.restore_backup(self._get_latest_backup())
    
    def _get_latest_backup(self) -> Optional[str]:
        """
        Get the path to the latest backup file.
        
        Returns:
            Optional[str]: Path to the latest backup file, or None if no backups exist
        """
        backup_dir = os.path.join(os.path.dirname(self.config_path), 'backups')
        if not os.path.exists(backup_dir):
            return None
            
        backup_files = [
            f for f in os.listdir(backup_dir)
            if f.endswith('.bak')
        ]
        
        if not backup_files:
            return None
            
        # Sort by modification time (newest first)
        backup_files.sort(
            key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)),
            reverse=True
        )
        
        return os.path.join(backup_dir, backup_files[0])
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key doesn't exist
            
        Returns:
            Any: Configuration value
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self._config[key] = value
        self.save_config() 