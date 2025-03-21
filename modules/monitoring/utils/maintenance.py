"""
Maintenance Utilities

This module provides utilities for system maintenance tasks like
log rotation, backup management, and cleanup operations.
"""

import os
import shutil
import logging
import json
from datetime import datetime, timedelta
from typing import List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class MaintenanceUtils:
    """Utilities for system maintenance tasks."""
    
    def __init__(self, base_dir: str = "data"):
        """
        Initialize maintenance utilities.
        
        Args:
            base_dir: Base directory for data storage
        """
        self.base_dir = Path(base_dir)
        self.backup_dir = self.base_dir / "backups"
        self.logs_dir = self.base_dir / "logs"
        self.temp_dir = self.base_dir / "temp"
        
        # Create necessary directories
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist."""
        for directory in [self.backup_dir, self.logs_dir, self.temp_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def rotate_logs(self, max_size_mb: int = 10, max_files: int = 5) -> None:
        """
        Rotate log files when they exceed the maximum size.
        
        Args:
            max_size_mb: Maximum size of log files in megabytes
            max_files: Maximum number of backup files to keep
        """
        try:
            log_file = self.logs_dir / "bot.log"
            if not log_file.exists():
                return
            
            # Check if log file exceeds max size
            if log_file.stat().st_size > max_size_mb * 1024 * 1024:
                # Rotate existing backup files
                for i in range(max_files - 1, 0, -1):
                    old_backup = self.logs_dir / f"bot.log.{i}"
                    new_backup = self.logs_dir / f"bot.log.{i + 1}"
                    if old_backup.exists():
                        if i == max_files - 1:
                            old_backup.unlink()  # Remove oldest backup
                        else:
                            old_backup.rename(new_backup)
                
                # Backup current log file
                backup_file = self.logs_dir / "bot.log.1"
                shutil.copy2(log_file, backup_file)
                
                # Clear current log file
                log_file.write_text("")
                
                logger.info(f"Rotated log file: {log_file}")
        except Exception as e:
            logger.error(f"Error rotating logs: {e}")
    
    def backup_config(self) -> Optional[str]:
        """
        Create a backup of all configuration files.
        
        Returns:
            str: Path to the backup file, or None if backup failed
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"config_backup_{timestamp}.zip"
            
            # Create a zip file containing all config files
            config_dir = Path("config")
            if config_dir.exists():
                shutil.make_archive(
                    str(backup_file.with_suffix("")),
                    "zip",
                    config_dir
                )
                logger.info(f"Created config backup: {backup_file}")
                return str(backup_file)
            else:
                logger.warning("Config directory not found")
                return None
        except Exception as e:
            logger.error(f"Error backing up config: {e}")
            return None
    
    def cleanup_temp_files(self, max_age_days: int = 7) -> int:
        """
        Clean up temporary files older than the specified age.
        
        Args:
            max_age_days: Maximum age of files to keep in days
            
        Returns:
            int: Number of files cleaned up
        """
        try:
            cleanup_count = 0
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            
            # Clean up temp directory
            for file in self.temp_dir.glob("*"):
                if file.is_file():
                    # Check file age
                    file_time = datetime.fromtimestamp(file.stat().st_mtime)
                    if file_time < cutoff_date:
                        file.unlink()
                        cleanup_count += 1
            
            logger.info(f"Cleaned up {cleanup_count} temporary files")
            return cleanup_count
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {e}")
            return 0
    
    def cleanup_old_backups(self, max_backups: int = 10) -> int:
        """
        Clean up old backup files, keeping only the specified number of recent backups.
        
        Args:
            max_backups: Maximum number of backup files to keep
            
        Returns:
            int: Number of backup files removed
        """
        try:
            cleanup_count = 0
            
            # Get list of backup files sorted by modification time
            backup_files = sorted(
                self.backup_dir.glob("config_backup_*.zip"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            # Remove excess backup files
            for backup_file in backup_files[max_backups:]:
                backup_file.unlink()
                cleanup_count += 1
            
            logger.info(f"Cleaned up {cleanup_count} old backup files")
            return cleanup_count
        except Exception as e:
            logger.error(f"Error cleaning up old backups: {e}")
            return 0
    
    def get_disk_usage(self) -> dict:
        """
        Get disk usage information for data directories.
        
        Returns:
            dict: Dictionary containing disk usage information
        """
        try:
            usage = {}
            for name, directory in [
                ("backups", self.backup_dir),
                ("logs", self.logs_dir),
                ("temp", self.temp_dir)
            ]:
                total_size = sum(
                    f.stat().st_size for f in directory.glob("**/*") if f.is_file()
                )
                usage[name] = {
                    "size_bytes": total_size,
                    "file_count": sum(1 for _ in directory.glob("**/*") if _.is_file())
                }
            
            return usage
        except Exception as e:
            logger.error(f"Error getting disk usage: {e}")
            return {}
    
    def list_backups(self) -> List[dict]:
        """
        List available configuration backups.
        
        Returns:
            List[dict]: List of backup information
        """
        try:
            backups = []
            for backup_file in self.backup_dir.glob("config_backup_*.zip"):
                stats = backup_file.stat()
                backups.append({
                    "filename": backup_file.name,
                    "size_bytes": stats.st_size,
                    "created_at": datetime.fromtimestamp(stats.st_mtime)
                })
            
            return sorted(backups, key=lambda x: x["created_at"], reverse=True)
        except Exception as e:
            logger.error(f"Error listing backups: {e}")
            return []
    
    def restore_config(self, backup_file: str) -> bool:
        """
        Restore configuration from a backup file.
        
        Args:
            backup_file: Name of the backup file to restore from
            
        Returns:
            bool: True if restore was successful, False otherwise
        """
        try:
            backup_path = self.backup_dir / backup_file
            if not backup_path.exists():
                logger.error(f"Backup file not found: {backup_file}")
                return False
            
            # Create a temporary directory for extraction
            temp_extract = self.temp_dir / "config_restore"
            if temp_extract.exists():
                shutil.rmtree(temp_extract)
            temp_extract.mkdir()
            
            # Extract backup
            shutil.unpack_archive(str(backup_path), str(temp_extract), "zip")
            
            # Backup current config
            current_backup = self.backup_config()
            
            # Replace current config
            config_dir = Path("config")
            if config_dir.exists():
                shutil.rmtree(config_dir)
            shutil.copytree(temp_extract, config_dir)
            
            # Clean up
            shutil.rmtree(temp_extract)
            
            logger.info(f"Restored config from backup: {backup_file}")
            return True
        except Exception as e:
            logger.error(f"Error restoring config: {e}")
            return False 