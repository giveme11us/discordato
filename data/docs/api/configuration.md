# Configuration API Documentation

## Overview

The configuration system manages bot settings through environment variables and module-specific configuration files.

## Core Configuration

### Environment Variables (`.env`)

```env
# Bot Configuration
DISCORD_BOT_TOKEN=your_bot_token
COMMAND_PREFIX=/
GUILD_IDS=guild_id1,guild_id2
DEV_GUILD_ID=dev_guild_id

# Performance Settings
SYNC_COOLDOWN=60
RETRY_BUFFER=5
MAX_RETRIES=3
BATCH_SIZE=25
CACHE_TTL=3600

# Module Settings
ENABLED_MODULES=mod,redeye
COMMAND_COOLDOWN=3
MAX_COMMANDS_PER_MINUTE=60

# Development Settings
DEBUG_LOGGING=True
```

## Settings Class

class Settings:
    """Container for all bot settings."""
    
    def __init__(self):
        # Discord API settings
        self.COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '/')
        self.GUILD_IDS = [int(id.strip()) for id in os.getenv('GUILD_IDS', '').split(',') if id.strip()]

        # Bot settings
        self.BOT_DESCRIPTION = "A modular Discord bot system"
        self.BOT_ACTIVITY = "Serving commands"

        # Module settings
        self.MODULES_PATH = "modules"
        self.ENABLED_MODULES = os.getenv('ENABLED_MODULES', 'mod,redeye').split(',')

        # Command settings
        self.COMMAND_COOLDOWN = int(os.getenv('COMMAND_COOLDOWN', '3'))
        self.MAX_COMMANDS_PER_MINUTE = int(os.getenv('MAX_COMMANDS_PER_MINUTE', '60'))

        # Performance settings
        self.SYNC_COOLDOWN = int(os.getenv('SYNC_COOLDOWN', '60'))
        self.RETRY_BUFFER = int(os.getenv('RETRY_BUFFER', '5'))
        self.MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
        self.BATCH_SIZE = int(os.getenv('BATCH_SIZE', '25'))
        self.CACHE_TTL = int(os.getenv('CACHE_TTL', '3600'))