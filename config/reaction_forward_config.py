"""
Reaction Forward Configuration

This module contains configuration settings for the reaction_forward feature.
"""

import os
from config import mod_config

# Whitelist of category IDs where messages will get a forward reaction
# Format: comma-separated list of category IDs
CATEGORY_IDS = [int(id) for id in os.getenv('REACTION_FORWARD_CATEGORY_IDS', '').split(',') if id]

# Whether the reaction forward feature is enabled
ENABLED = os.getenv('REACTION_FORWARD_ENABLED', 'True').lower() in ('true', '1', 't')

# The emoji to use for the forward reaction
FORWARD_EMOJI = "➡️"  # Unicode arrow_forward emoji

# Whether to enable the message forwarding feature when a user reacts with the forward emoji
ENABLE_FORWARDING = os.getenv('REACTION_FORWARD_ENABLE_FORWARDING', 'True').lower() in ('true', '1', 't')

# Title for forwarded message embeds
FORWARD_TITLE = os.getenv('REACTION_FORWARD_TITLE', 'Forwarded Message')

# Use the module-wide whitelist for role permissions
WHITELIST_ROLE_IDS = mod_config.WHITELIST_ROLE_IDS

# Blacklist of channel IDs that should be ignored even if they are in a whitelisted category
# Format: comma-separated list of channel IDs
BLACKLIST_CHANNEL_IDS = [int(id) for id in os.getenv('REACTION_FORWARD_BLACKLIST_CHANNEL_IDS', '').split(',') if id] 