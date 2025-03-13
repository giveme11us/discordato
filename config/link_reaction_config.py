"""
Link Reaction Configuration

This module contains configuration settings for the link_reaction feature.
"""

import os
from config import mod_config

# Whitelist of category IDs where messages will get a link reaction
# Format: comma-separated list of category IDs
CATEGORY_IDS = [int(id) for id in os.getenv('LINK_REACTION_CATEGORY_IDS', '').split(',') if id]

# Whether the link reaction feature is enabled
ENABLED = os.getenv('LINK_REACTION_ENABLED', 'True').lower() in ('true', '1', 't')

# The emoji to use for the link reaction
LINK_EMOJI = "🔗"  # Unicode link emoji

# Use the module-wide whitelist for role permissions
WHITELIST_ROLE_IDS = mod_config.WHITELIST_ROLE_IDS

# Blacklist of channel IDs that should be ignored even if they are in a whitelisted category
# Format: comma-separated list of channel IDs
BLACKLIST_CHANNEL_IDS = [int(id) for id in os.getenv('LINK_REACTION_BLACKLIST_CHANNEL_IDS', '').split(',') if id]

# Supported stores for product ID extraction
# The link reaction will only be added to embeds from these stores
# Currently supported stores:
# - LUISAVIAROMA: Product IDs are extracted from the URL or PID field
# To add more stores, update the process_message and handle_reaction_add functions in link_reaction.py 