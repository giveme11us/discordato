#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct Settings Initialization

This script directly creates the settings files without importing any config modules,
avoiding potential circular import issues.
"""

import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('direct_initialize')

# Settings directory
SETTINGS_DIR = os.path.join('data', 'settings')

# Default settings for each module
KEYWORD_FILTER_DEFAULTS = {
    "ENABLED": True,
    "DRY_RUN": False,
    "NOTIFICATION_CHANNEL_ID": None,
    "NOTIFY_FILTERED": True,
    "CATEGORY_IDS": [],
    "BLACKLIST_CHANNEL_IDS": [],
    "FILTERS": {
        "scam_links": {
            "enabled": True,
            "patterns": [
                "discord\\.gift\\/[a-zA-Z0-9]+",
                "nitro\\s+for\\s+free",
                "free\\s+nitro\\s+generator",
                "steam\\s+community\\.com\\/tradeoffer"
            ],
            "description": "Filters common Discord nitro scam patterns",
            "action": "notify",
            "severity": "high"
        },
        "invite_links": {
            "enabled": True,
            "patterns": [
                "discord\\.gg\\/[a-zA-Z0-9]+",
                "discordapp\\.com\\/invite\\/[a-zA-Z0-9]+"
            ],
            "description": "Filters Discord server invite links",
            "action": "notify",
            "severity": "medium"
        },
        "inappropriate_content": {
            "enabled": True,
            "patterns": [
                "(^|\\s)nsfw(\\s|$)",
                "(^|\\s)18\\+(\\s|$)"
            ],
            "description": "Filters inappropriate content references",
            "action": "log",
            "severity": "medium"
        }
    }
}

LINK_REACTION_DEFAULTS = {
    "ENABLED": True,
    "CATEGORY_IDS": [],
    "BLACKLIST_CHANNEL_IDS": [],
    "LINK_EMOJI": "🔗",
    "STORES": {
        "luisaviaroma": {
            "enabled": True,
            "name": "LUISAVIAROMA",
            "description": "Extract product IDs from LUISAVIAROMA embeds",
            "file_path": "data/luisaviaroma_drop_urls.txt",
            "detection": {
                "type": "author_name",
                "value": "LUISAVIAROMA"
            },
            "extraction": {
                "primary": "url",
                "pattern": "\\/[^\\/]+\\/([^\\/]+)$",
                "fallback": "field_pid"
            }
        }
    }
}

REACTION_FORWARD_DEFAULTS = {
    "ENABLED": True,
    "CATEGORY_IDS": [],
    "BLACKLIST_CHANNEL_IDS": [],
    "FORWARD_EMOJI": "➡️",
    "ENABLE_FORWARDING": True,
    "FORWARD_TITLE": "Forwarded Message",
    "DESTINATION_CHANNEL_ID": None,
    "FORWARD_ATTACHMENTS": True,
    "FORWARD_EMBEDS": True
}

PINGER_DEFAULTS = {
    "ENABLED": True,
    "NOTIFICATION_CHANNEL_ID": None,
    "NOTIFICATION_TITLE": "IMPORTANT PING",
    "MONITOR_EVERYONE": True,
    "MONITOR_HERE": True,
    "MONITOR_ROLES": False,
    "EMBED_COLOR": 0xFF0000,
    "INCLUDE_JUMP_LINK": True
}

# Map of module names to default settings
MODULE_DEFAULTS = {
    "keyword_filter": KEYWORD_FILTER_DEFAULTS,
    "link_reaction": LINK_REACTION_DEFAULTS,
    "reaction_forward": REACTION_FORWARD_DEFAULTS,
    "pinger": PINGER_DEFAULTS
}

def create_settings_files():
    """Create the settings files directly."""
    # Create settings directory if it doesn't exist
    os.makedirs(SETTINGS_DIR, exist_ok=True)
    logger.info(f"Settings directory: {SETTINGS_DIR}")
    
    # Create each module's settings file
    for module_name, defaults in MODULE_DEFAULTS.items():
        settings_file = os.path.join(SETTINGS_DIR, f"{module_name}.json")
        
        try:
            # Write default settings directly to file
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(defaults, f, indent=2)
                
            logger.info(f"Created settings file for {module_name}")
        except Exception as e:
            logger.error(f"Error creating settings file for {module_name}: {e}")

if __name__ == "__main__":
    create_settings_files()
    logger.info("Settings files created successfully") 