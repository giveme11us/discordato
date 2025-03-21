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

# Module Settings
ENABLED_MODULES=mod,redeye
COMMAND_COOLDOWN=3
MAX_COMMANDS_PER_MINUTE=60

# Development Settings
DEBUG_LOGGING=True
```

### Core Settings (`config/core/settings.py`)

```python
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
```

## Module Configuration

### Mod Module Settings

```python
# Keyword Filter Configuration
FILTER_DEFAULT_CONFIG = {
    "ENABLED": False,
    "DRY_RUN": True,
    "CATEGORY_IDS": [],
    "MONITOR_CHANNEL_IDS": [],
    "BLACKLIST_CHANNEL_IDS": [],
    "NOTIFICATION_CHANNEL_ID": None,
    "FILTERS": {
        "spam": {
            "enabled": True,
            "patterns": [],
            "action": "delete",
            "notify": True
        }
    }
}

# Forward System Configuration
FORWARD_DEFAULT_CONFIG = {
    "ENABLED": False,
    "CATEGORY_IDS": [],
    "BLACKLIST_CHANNEL_IDS": [],
    "DESTINATION_CHANNEL_ID": None,
    "FORWARD_EMOJI": "➡️"
}
```

### Settings Management

The bot provides a settings management script (`manage_settings.py`) for handling configuration:

```bash
# Export settings
python manage_settings.py export output.json

# Import settings
python manage_settings.py import input.json --module mod

# List current settings
python manage_settings.py list --module mod

# Validate settings
python manage_settings.py validate

# Reset settings
python manage_settings.py reset --module mod
```

## Configuration Access

### Settings Manager Pattern

```python
from config.core.settings_manager import get_manager

# Get module-specific settings manager
settings = get_manager('mod')

# Access settings
enabled = settings.get('ENABLED', False)
channels = settings.get('CHANNELS', [])

# Update settings
settings.set('ENABLED', True)
settings.set('CHANNELS', [channel_id])
```

### Error Handling

```python
from core.error_handler import ConfigurationError

try:
    settings.validate()
except ConfigurationError as e:
    logger.error(f"Configuration error: {e}")
```

## Best Practices

### 1. Environment Variables
- Use for sensitive data
- Include in .env.example
- Document all variables
- Validate on load

### 2. Module Settings
- Use type hints
- Provide defaults
- Validate values
- Document options

### 3. Security
- Never commit tokens
- Use environment variables for secrets
- Implement permission checks
- Validate all inputs

### 4. Maintenance
- Regular validation
- Keep documentation updated
- Monitor for issues
- Backup configurations

## Notes

- Always validate configuration
- Use environment variables for sensitive data
- Keep module settings separate
- Document all options
- Implement proper error handling
