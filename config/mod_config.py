"""
Mod Module Configuration

This module contains shared configuration settings for all features within the mod module.
"""

import os

# IMPORTANT: Whitelist of role IDs that CAN trigger privileged actions
# ONLY users with these roles can perform privileged actions like using @everyone/@here
# Format: comma-separated list of role IDs
WHITELIST_ROLE_IDS = [int(id) for id in os.getenv('MOD_WHITELIST_ROLE_IDS', '').split(',') if id]

# If MOD_WHITELIST_ROLE_IDS is not set, fall back to PINGER_WHITELIST_ROLE_IDS for backward compatibility
if not WHITELIST_ROLE_IDS:
    WHITELIST_ROLE_IDS = [int(id) for id in os.getenv('PINGER_WHITELIST_ROLE_IDS', '').split(',') if id] 