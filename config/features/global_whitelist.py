"""
Global Whitelist Configuration

This module provides a common whitelist of role IDs
that is used across multiple modules.
"""

import os
import logging
from typing import Set

logger = logging.getLogger('discord_bot.config.global_whitelist')

class WhitelistConfig:
    """Configuration class for global whitelist settings."""
    
    def __init__(self):
        # Comma-separated list of role IDs that CAN trigger privileged actions in all mod module features
        self.MOD_WHITELIST_ROLE_IDS_STR = os.environ.get('MOD_WHITELIST_ROLE_IDS', '')
        
        # Parse into a set of integers
        self._whitelist_role_ids: Set[int] = set()
        try:
            if self.MOD_WHITELIST_ROLE_IDS_STR:
                self._whitelist_role_ids = {int(role_id.strip()) for role_id in self.MOD_WHITELIST_ROLE_IDS_STR.split(',') if role_id.strip()}
            
            logger.info(f"Loaded global whitelist role IDs: {self._whitelist_role_ids}")
        except Exception as e:
            logger.error(f"Error parsing MOD_WHITELIST_ROLE_IDS: {e}")
    
    @property
    def WHITELIST_ROLE_IDS(self) -> Set[int]:
        """Get the set of whitelisted role IDs."""
        return self._whitelist_role_ids
    
    @WHITELIST_ROLE_IDS.setter
    def WHITELIST_ROLE_IDS(self, value: Set[int]):
        """Set the whitelisted role IDs."""
        self._whitelist_role_ids = set(value)
        self.MOD_WHITELIST_ROLE_IDS_STR = ','.join(str(role_id) for role_id in value)
        logger.info(f"Updated global whitelist role IDs: {self._whitelist_role_ids}")

# Create and export the config instance
whitelist = WhitelistConfig() 