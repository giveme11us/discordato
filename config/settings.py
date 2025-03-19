"""
General Configuration Settings

This module contains general configuration settings for the Discord bot.
"""

import os

# Discord API settings
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '/')
# Handle GUILD_IDS more robustly to handle potential spacing issues
guild_ids_str = os.getenv('GUILD_IDS', '')
GUILD_IDS = [int(id.strip()) for id in guild_ids_str.split(',') if id.strip()]

# Bot settings
BOT_DESCRIPTION = "A modular Discord bot system"
BOT_ACTIVITY = "Serving commands"

# Module settings
MODULES_PATH = "modules"
ENABLED_MODULES = os.getenv('ENABLED_MODULES', 'mod,online,instore,redeye').split(',')

# Command settings
COMMAND_COOLDOWN = int(os.getenv('COMMAND_COOLDOWN', '3'))  # seconds
MAX_COMMANDS_PER_MINUTE = int(os.getenv('MAX_COMMANDS_PER_MINUTE', '60'))

# Error messages
ERROR_MESSAGES = {
    'command_not_found': "Command not found. Type {prefix}help for a list of commands.",
    'permission_denied': "You don't have permission to use this command.",
    'cooldown': "Please wait {time} seconds before using this command again.",
    'general_error': "An error occurred while processing your command."
}

# Development settings
DEV_GUILD_ID = os.getenv('DEV_GUILD_ID', None)
if DEV_GUILD_ID and DEV_GUILD_ID.isdigit():
    DEV_GUILD_ID = int(DEV_GUILD_ID)
else:
    DEV_GUILD_ID = None 