"""
Pinger Configuration

This module contains configuration settings for the pinger feature.
"""

import os
from config import mod_config

# Notification channel ID for sending ping notifications
# The channel where the bot will send notifications about @everyone and @here pings
NOTIFICATION_CHANNEL_ID = os.getenv('PINGER_NOTIFICATION_CHANNEL_ID', None)
if NOTIFICATION_CHANNEL_ID and NOTIFICATION_CHANNEL_ID.isdigit():
    NOTIFICATION_CHANNEL_ID = int(NOTIFICATION_CHANNEL_ID)

# IMPORTANT: Whitelist of role IDs that CAN trigger notifications
# ONLY users with these roles can use @everyone and @here to generate notifications
# Using the module-wide whitelist from mod_config
WHITELIST_ROLE_IDS = mod_config.WHITELIST_ROLE_IDS

# Settings for the notification
NOTIFICATION_TITLE = "IMPORTANT PING"

# Whether to monitor @everyone pings
MONITOR_EVERYONE = os.getenv('PINGER_MONITOR_EVERYONE', 'True').lower() in ('true', '1', 't')

# Whether to monitor @here pings
MONITOR_HERE = os.getenv('PINGER_MONITOR_HERE', 'True').lower() in ('true', '1', 't')

# Whether to monitor role pings
MONITOR_ROLES = os.getenv('PINGER_MONITOR_ROLES', 'False').lower() in ('true', '1', 't') 