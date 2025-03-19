"""
Global Whitelist Configuration

This module provides a common whitelist of role IDs
that is used across multiple modules.
"""

import os
import logging
from typing import Set

logger = logging.getLogger('discord_bot.config.global_whitelist')

# Comma-separated list of role IDs that CAN trigger privileged actions in all mod module features
MOD_WHITELIST_ROLE_IDS_STR = os.environ.get('MOD_WHITELIST_ROLE_IDS', '')

# Parse into a set of integers
WHITELIST_ROLE_IDS: Set[int] = set()
try:
    if MOD_WHITELIST_ROLE_IDS_STR:
        WHITELIST_ROLE_IDS = {int(role_id.strip()) for role_id in MOD_WHITELIST_ROLE_IDS_STR.split(',') if role_id.strip()}
    
    logger.info(f"Loaded global whitelist role IDs: {WHITELIST_ROLE_IDS}")
except Exception as e:
    logger.error(f"Error parsing MOD_WHITELIST_ROLE_IDS: {e}") 