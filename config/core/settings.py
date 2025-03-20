"""
General Configuration Settings

This module contains general configuration settings for the Discord bot.
"""

import os

class Settings:
    """Container for all bot settings."""
    
    def __init__(self):
        # Discord API settings
        self.COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '/')
        # Handle GUILD_IDS more robustly to handle potential spacing issues
        guild_ids_str = os.getenv('GUILD_IDS', '')
        self.GUILD_IDS = [int(id.strip()) for id in guild_ids_str.split(',') if id.strip()]

        # Bot settings
        self.BOT_DESCRIPTION = "A modular Discord bot system"
        self.BOT_ACTIVITY = "Serving commands"

        # Module settings
        self.MODULES_PATH = "modules"
        self.ENABLED_MODULES = os.getenv('ENABLED_MODULES', 'mod,online,instore,redeye').split(',')

        # Command settings
        self.COMMAND_COOLDOWN = int(os.getenv('COMMAND_COOLDOWN', '3'))  # seconds
        self.MAX_COMMANDS_PER_MINUTE = int(os.getenv('MAX_COMMANDS_PER_MINUTE', '60'))

        # Error messages
        self.ERROR_MESSAGES = {
            'command_not_found': "Command not found. Type {prefix}help for a list of commands.",
            'permission_denied': "You don't have permission to use this command.",
            'cooldown': "Please wait {time} seconds before using this command again.",
            'general_error': "An error occurred while processing your command."
        }

        # Development settings
        dev_guild_id = os.getenv('DEV_GUILD_ID', None)
        self.DEV_GUILD_ID = int(dev_guild_id) if dev_guild_id and dev_guild_id.isdigit() else None

# Create and export the settings instance
settings = Settings() 